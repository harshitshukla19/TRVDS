from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Evidence, FIR, Challan, Profile, MemoEvidence, DetectionBoundary
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .ai_utils import analyze_evidence
from django.conf import settings
import os, json
from django.http import JsonResponse
from .forms import LoginForm, SignupForm, ProfileForm
from django.contrib.auth.models import User
from django.forms.models import model_to_dict

# --- PUBLIC PAGES ---

def index(request):
    return render(request, 'index.html')

def check_challan(request):
    challan = None
    error = None
    v_no = None
    if request.method == "POST":
        # Logic to check database
        v_no = request.POST.get('vehicle_number',"").upper()
        # Filter DB (Case insensitive)
        if v_no:
            try:
              challan = Challan.objects.get(vehicle_number__iexact=v_no, status = "unpaid")
            except Challan.DoesNotExist:
                error = "No unpaid found for this vehical."
    return render(request, 'challan.html', {'challan': challan, 'vehical_number': v_no, "error": error})
# return render(request, 'challan.html')

def admin_login(request):
    return render(request, 'admin-login.html')

def about_page(request):
    return render(request, 'about.html')

# --- USER PAGES ---

@login_required
def upload_evidence(request):
    if request.method == "POST":
        video = request.FILES.get('file')
        loc = request.POST.get('location')
        desc = request.POST.get('description')
        
        # Save to DB
        evidence = Evidence.objects.create(user=request.user, file=video, location=loc, description=desc)
        
        # Trigger AI Analysis (In real world, use Celery task queue)
        # For localhost, we run it directly (might take time)
        video_path = os.path.join(settings.MEDIA_ROOT, evidence.file.name)
        ai_result = analyze_evidence(video_path)
        
        # Update DB with AI results
        evidence.is_fake = ai_result['is_fake']
        if ai_result['violations']:
            evidence.violation_type = ", ".join(ai_result['violations'])
        evidence.save()

        return redirect('user_dashboard')
    return render(request, 'upload.html')

@login_required
def file_fir(request):
    if request.method == "POST":
        # Handle FIR saving logic here...
        pass
    return render(request, 'fir.html')


# --- ADMIN PAGES ---

def admin_login(request):
    # Standard Django Login Logic
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin-dashboard.html')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'admin-login.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('index')
    
    # Analytics Data
    total_violations = Challan.objects.count()
    pending_memos = Evidence.objects.filter(is_verified=False).count()
    
    context = {
        'total_violations': total_violations,
        'pending_memos': pending_memos,
        'evidence_list': Evidence.objects.filter(is_verified=False)
    }
    return render(request, 'admin-dashboard.html', context)

@login_required
def memo_verification(request):
    pending_memos = Evidence.objects.filter(status='Pending').order_by('-uploaded_at')
    reviewed_memos = Evidence.objects.exclude(status='Pending').order_by('-uploaded_at')

    return render(request, 'memo-verification.html', {
        'pending_memos': pending_memos,
        'reviewed_memos': reviewed_memos
    })


@login_required
def verify_memo(request, memo_id):
    memo = get_object_or_404(Evidence, memo_id=memo_id)
    memo.status = 'Verified'
    memo.save()
    return redirect('memo_verification')


@login_required
def reject_memo(request, memo_id):
    memo = get_object_or_404(Evidence, memo_id=memo_id)
    memo.status = 'Rejected'
    memo.save()
    return redirect('memo_verification')

def evidence_verification(request, memo_id):
    evidence = get_object_or_404(Evidence, memo_id=memo_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action in ["Verified", "Rejected"]:
            evidence.status = action
            evidence.save()
            messages.success(request, f"Evidence marked as {action}")
            return redirect("evidence_verification", memo_id=memo_id)

    file_name = evidence.file.name if evidence.file else ""

    is_video = file_name.lower().endswith(('.mp4', '.webm', '.mov'))
    is_image = file_name.lower().endswith(('.jpg', '.jpeg', '.png'))

    context = {
        'evidence': evidence,
        'is_video': is_video,
        'is_image': is_image,
    }

    return render(request, "evidence-verification.html", context)


def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_profiles(request):
    admins = User.objects.filter(is_staff=True)

    context = {
        "admins": admins
    }
    return render(request, "admin-profiles.html", context)

@login_required
def vehicle_listings(request):
    vehicles = Challan.objects.all().order_by('-date')
    return render(request, 'vehicle-listings.html', {'vehicles': vehicles})

@login_required
def boundary_creation(request):
    if request.method == "POST":
        DetectionBoundary.objects.create(
            name=request.POST.get('name'),
            start_point=request.POST.get('start_point'),
            end_point=request.POST.get('end_point'),
            length_km=request.POST.get('length'),
            created_by=request.user
        )
        messages.success(request, "Boundary created successfully")
        return redirect('boundary_creation')

    boundaries = DetectionBoundary.objects.all().order_by('-created_at')
    return render(
        request,
        'boundary-creation.html',
        {'boundaries': boundaries}
    )

# --- USER Login & Signup ---

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                username = User.objects.get(email=email).username
            except User.DoesNotExist:
                return JsonResponse({'error': 'User does not exist'})

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return JsonResponse({'success': True})
            return JsonResponse({'error': 'Invalid credentials'})

    return render(request, 'user-login.html', {'form': LoginForm()})

def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            # return JsonResponse({'success': True})
            return render(request, 'user-login.html', {'success': True})
        return JsonResponse({'error': form.errors.as_json()})

    return render(request, 'user-signup.html', {'form': SignupForm()})

def user_logout(request):
    logout(request)
    return render(request, 'index.html', {'success': True})

# --- USER DASHBOARD & FEATURES ---

@login_required
def user_dashboard(request):
    # Fetch data for the dashboard cards
    recent_violations = Evidence.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
    
    # Ensure profile exists (safe check)
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    context = {
        'user': request.user,
        'coins': profile.coins,
        'recent_violations': recent_violations,
        'certificate_unlocked': profile.certificate_unlocked
    }
    return render(request, 'user-dashboard.html', context)

@login_required
def upload_evidence(request):
    if request.method == "POST":
        file = request.FILES.get('file') # Matches <input type="file" name="file">
        loc = request.POST.get('location')
        desc = request.POST.get('description')
        
        if file:
            # Create Evidence and Award Coins
            Evidence.objects.create(user=request.user, file=file, location=loc, description=desc)
            
            # Add Coins Logic
            profile = request.user.profile
            profile.coins += 10
            if profile.coins >= 100:
                profile.certificate_unlocked = True
            profile.save()
            
            messages.success(request, "Evidence Uploaded! +10 Coins Earned")
            return redirect('user_dashboard')
            
    return render(request, 'upload.html')

@login_required
def violations_history(request):
    # Show full list of uploaded evidence/violations
    history = Evidence.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'violations.html', {'history': history})

@login_required
def rewards_page(request):
    return render(request, 'rewards.html', {'profile': request.user.profile})

@login_required
def file_fir_view(request):
    if request.method == "POST":
        loc = request.POST.get('location')
        desc = request.POST.get('description')
        img = request.FILES.get('fir_image')
        FIR.objects.create(user=request.user, location=loc, description=desc, file=img)
        messages.success(request, "FIR Submitted Successfully")
        return redirect('user_dashboard')
    return render(request, 'fir.html')

@login_required
def profile(request):
    # Ensure a profile exists for the user (safety check)
    user=request.user
    
    if request.method == "POST":
        user.first_name = request.POST.get("first_name", "").strip()
        user.location = request.POST.get("location", "").strip()
        user.phone = request.POST.get("phone", "").strip()
        user.avtar = request.POST.get("avtar", "").strip()
        user.email = request.POST.get("email", "").strip()

        # Ensure NOT NULL fields never receive None
        if not user.first_name:
            user.first_name = ""

        user.save()
        
        # Update Profile Model
        
        messages.success(request, "Profile Updated Successfully!")
        return redirect('profile') # Refresh the page

    return render(request, 'profile.html', {'user': user, })