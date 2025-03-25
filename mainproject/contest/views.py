from django.shortcuts import render,get_object_or_404, redirect
from .models import Contest, Participation
from .models import Submission
from .forms import SubmissionForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

def landing_view(request):
    # Check if logged in or not
    if request.user.is_authenticated:
        return redirect('contest/')
    else:
        return render(request, 'landing.html')

def index_view(request):
    #retirve contest from database
    contests = Contest.objects.all()
    return render(request, 'contest/index.html', {'contests': contests})



@login_required
def contest_view(request, contest_id):
    # Retrieve previous submission (if exists)
    submission = Submission.objects.filter(contest_id=contest_id, user_id=request.user).first()
    contest = Contest.objects.filter(id=contest_id).first()
    has_participated = Participation.objects.filter(user_id=request.user, contest_id=contest).exists()

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


    

    return render(request, "contest/contest.html", {"submission": submission, "contest": contest, "has_participated": has_participated})


@login_required
def participate(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    user = request.user

    # Check if the user has already participated
    if Participation.objects.filter(user_id=user, contest_id=contest).exists():
        messages.warning(request, "You have already participated in this contest.")
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