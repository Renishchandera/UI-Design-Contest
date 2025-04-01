from django.shortcuts import render,get_object_or_404, redirect
from .models import Contest, Participation
from .models import Submission, User
from .forms import SubmissionForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
# Create your views here.

def landing_view(request):
    # Check if logged in or not
    if request.user.is_authenticated:
        return redirect('contest/')
    else:
        return render(request, 'landing.html')
@login_required
def index_view(request):
    #retirve contest from database
    contests = Contest.objects.all()
    return render(request, 'contest/index.html', {"user": request.user,'contests': contests})



@login_required
def contest_view(request, contest_id):
    # Retrieve previous submission (if exists)
    submission = Submission.objects.filter(contest_id=contest_id, user_id=request.user).first()
    contest = Contest.objects.filter(id=contest_id).first()
    has_participated = Participation.objects.filter(user_id=request.user, contest_id=contest).exists()
    total_participations = Participation.objects.filter(contest_id=contest_id).count()
    is_ended = timezone.now() >= contest.end_date
    if request.method == "POST":
        html_code = request.POST.get("html_code")
        css_code = request.POST.get("css_code")

        Submission.objects.update_or_create(
            contest_id_id=contest_id,
            user_id=request.user,
            defaults={"html_code": html_code, "css_code": css_code}
        )
        # update participation status and update submission id
        Participation.objects.update_or_create(
            user_id=request.user,   # Lookup field (searches for an existing Participation)
            contest_id=contest,     # Lookup field (used to find the existing record)
            defaults={
                "status": True,           # If found, update status to True (submission done)
                "submission_id": submission  # Update or set the submission reference
            }
        )
        messages.success(request, "Code Submitted Successfully")

        return redirect(request.path)  # Redirect to prevent form resubmission


    

    return render(request, "contest/contest.html", {"user": request.user,"submission": submission, "contest": contest, "has_participated": has_participated,"current_participations": total_participations, "is_ended": is_ended})


@login_required
def participate(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    user = request.user

    # Check if the user has already participated
    if Participation.objects.filter(user_id=user, contest_id=contest).exists():
        messages.error(request, "You have already participated in this contest.")
        return redirect('contest_view', contest_id=contest.id)

    # Check if the contest has reached its participation limit
    if Participation.objects.filter(contest_id=contest).count() >= contest.limit:
        messages.error(request, "Participation limit reached for this contest.")
        return redirect('contest_view', contest_id=contest.id)

    # Check if the user has enough coins to participate
    if user.coins < contest.entry_fee:
        messages.error(request, "You do not have enough coins to participate.")
        return redirect('contest_view', contest_id=contest.id)

    # Deduct entry fee and register participation
    user.coins -= contest.entry_fee
    user.save()

    Participation.objects.create(user_id=user, contest_id=contest, status=False)

    messages.success(request, "You have successfully participated in the contest!")
    return redirect('contest_view', contest_id=contest.id)

# Profile view
@login_required
def profile_view(request, user_id):
    user = request.user
    if(user.id == user_id):
        submissions = Submission.objects.filter(user_id=user)
        participations = Participation.objects.filter(user_id=user)
        # get all contests user participated
        coins = user.coins

        return render(request, "contest/profile.html", {"user": user, "submissions": submissions})
    else:
        return redirect('index_view')
    
@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')  # Redirect back to profile page
    else:
        messages.error(request, "Invalid request.")
        return redirect('profile')
 
@login_required   
def mycontests_view(request):
    user = request.user

    participated_contests = Contest.objects.filter(participation__user_id=request.user)

    return render(request, "contest/mycontests.html", {"user": user, "contests": participated_contests})

@login_required
def show_voting_view(request):
    now = timezone.now()
    three_days_ago = now - timedelta(days=3)

    # Contests whose end_date is within the last 3 days (Voting open)
    voting_open_contests = Contest.objects.filter(end_date__gte=three_days_ago, end_date__lte=now)

    # Contests whose end_date is more than 3 days ago (Voting closed)
    voting_closed_contests = Contest.objects.filter(end_date__lt=three_days_ago)

    return render(request, "contest/show_voting_page.html", {
        "voting_open_contests": voting_open_contests,
        "voting_closed_contests": voting_closed_contests,
    })
    
@login_required
def voting_view(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    user = request.user
    now = timezone.now()
    voting_end_time = contest.end_date + timedelta(days=3)  # Voting lasts 3 days after contest ends
    
    # Check if voting is still open
    voting_open = now <= voting_end_time
     # Fetch all submissions for this contest
    submissions = Submission.objects.filter(contest_id=contest).order_by('-votes')
     # Get top 3 winners
    top_winners = list(submissions[:3])

     # Calculate Prize Pool
    total_participants = Submission.objects.filter(contest_id=contest).count()
    entry_fee = contest.entry_fee  # Assuming entry_fee is stored in Contest model
    prize_pool = total_participants * entry_fee  # Total prize pool

    # Calculate individual rewards
    rewards = {
        "first": int(prize_pool * 0.50),
        "second": int(prize_pool * 0.30),
        "third": int(prize_pool * 0.20)
    }


    # Get remaining submissions (excluding top 3)
    other_submissions = submissions
    return render(
        request, "contest/voting.html",
        {
        "contest": contest,
        "top_winners": top_winners,
        "other_submissions": other_submissions,
        "voting_open": voting_open,
        "voting_end_time": voting_end_time,
        "prize_pool": prize_pool,
        "rewards": rewards
        }
    )

@login_required
def vote_submission(request, submission_id):
    if request.method == "POST":
        submission = get_object_or_404(Submission, id=submission_id)
        user = request.user

        # Check if the user has already voted
        if submission in user.voted_submissions.all():
            messages.error(request, "You have already voted for this submission.")
        else:
            # Add submission to user's voted list
            user.voted_submissions.add(submission)
            submission.votes += 1
            submission.save()
            messages.success(request, "Your vote has been counted.")

    return redirect(request.META.get("HTTP_REFERER", "voting_page"))


@login_required
def claim_reward(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Check if voting has ended
    now = timezone.now()
    voting_end_time = submission.contest_id.end_date + timedelta(days=3)
    
    if now < voting_end_time:
        messages.error(request, "You can only claim rewards after voting ends.")
        return redirect('voting_view', contest_id=submission.contest_id.id)

    # Check if the user is eligible to claim
    submissions = Submission.objects.filter(contest_id=submission.contest_id).order_by('-votes')
    top_winners = list(submissions[:3])

    if submission not in top_winners:
        messages.error(request, "You are not in the top 3 winners.")
        return redirect('voting_view', contest_id=submission.contest_id.id)

    # Check if already claimed
    if submission.claimed_reward:
        messages.error(request, "You have already claimed your reward.")
        return redirect('voting_view', contest_id=submission.contest_id.id)

    # Determine the reward amount
    total_participants = Submission.objects.filter(contest_id=submission.contest_id).count()
    entry_fee = submission.contest_id.entry_fee
    prize_pool = total_participants * entry_fee

    position = top_winners.index(submission) + 1
    if position == 1:
        reward = int(prize_pool * 0.50)
    elif position == 2:
        reward = int(prize_pool * 0.30)
    else:
        reward = int(prize_pool * 0.20)

    # Mark reward as claimed
    submission.claimed_reward = True
    submission.save()

    # Assuming user has a 'coins' field to store rewards
    submission.user_id.coins += reward
    submission.user_id.save()

    messages.success(request, f"🎉 Reward of {reward} coins has been added to your account!")
    return redirect('voting_view', contest_id=submission.contest_id.id)