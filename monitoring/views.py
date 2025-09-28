import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .decorators import admin_required, user_required
from .mixins import IsAdminUser, RoleBasedPermission
from .models import Reading, User


def home_view(request):
    """Public home page"""
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "monitoring/home.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role", "user")

        errors = []

        # Validation
        if not username:
            errors.append("Username is required")
        if not email:
            errors.append("Email is required")
        if not password1:
            errors.append("Password is required")
        if password1 != password2:
            errors.append("Passwords do not match")
        if role not in ["admin", "user"]:
            errors.append("Invalid role")
        if User.objects.filter(username=username).exists():
            errors.append("Username already exists")
        if User.objects.filter(email=email).exists():
            errors.append("Email already exists")
        if len(password1) < 6:
            errors.append("Password must be at least 6 characters")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(
                request,
                "registration/register.html",
                {"username": username, "email": email, "role": role},
            )

        try:
            User.objects.create_user(
                username=username, email=email, password=password1, role=role
            )
            messages.success(request, "Đăng ký thành công! Hãy đăng nhập.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Đăng ký thất bại: {str(e)}")
            return render(
                request,
                "registration/register.html",
                {"username": username, "email": email, "role": role},
            )

    return render(request, "registration/register.html")


# Đăng nhập
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get("next", request.GET.get("next", "dashboard"))
            messages.success(
                request, f"Đăng nhập thành công! Chào mừng {user.username}."
            )
            return redirect(next_url)
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


# Đăng xuất
def logout_view(request):
    logout(request)
    messages.success(request, "Đã đăng xuất thành công.")
    return redirect("home")


# Dashboard với phân quyền
@login_required
@user_required
def dashboard_view(request):
    user_role = request.user.role
    latest_readings = Reading.objects.order_by("-timestamp")[:20]
    chart_data = []
    if latest_readings:
        for reading in latest_readings[:10]:
            chart_data.append(
                {
                    "timestamp": reading.timestamp.strftime("%H:%M:%S"),
                    "ph": float(reading.ph),
                    "tds": float(reading.tds),
                    "ntu": float(reading.ntu),
                }
            )
        chart_data.reverse()

    context = {
        "user_role": user_role,
        "is_admin": user_role == "admin",
        "latest_readings": latest_readings,
        "chart_data": json.dumps(chart_data),
    }
    return render(request, "monitoring/dashboard.html", context)


@login_required
@admin_required
def admin_dashboard_view(request):
    users = User.objects.all()
    return render(request, "monitoring/admin_dashboard.html", {"users": users})


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = (
                f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"
            )
            subject = "Đặt lại mật khẩu - Water Monitor"
            message = f"""
            Xin chào {user.username},
            Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản Water Monitor.
            Vui lòng click vào liên kết sau để đặt lại mật khẩu:
            {reset_url}
            Liên kết này sẽ hết hạn trong 24 giờ.
            Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
            Trân trọng,
            Đội ngũ Water Monitor
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(
                request,
                (
                    "Email đặt lại mật khẩu đã được gửi! "
                    "Vui lòng kiểm tra hộp thư của bạn."
                ),
            )
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "Email không tồn tại trong hệ thống")

    return render(request, "registration/password_reset_request.html")


# Đặt lại mật khẩu
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            if request.method == "POST":
                password = request.POST.get("password")
                password_confirm = request.POST.get("password_confirm")

                if password == password_confirm:
                    if len(password) < 6:
                        messages.error(request, "Mật khẩu phải có ít nhất 6 ký tự")
                        return render(
                            request, "registration/password_reset_confirm.html"
                        )

                    user.set_password(password)
                    user.save()
                    messages.success(
                        request,
                        "Mật khẩu đã được đặt lại thành công! Vui lòng đăng nhập.",
                    )
                    return redirect("login")
                else:
                    messages.error(request, "Mật khẩu xác nhận không khớp")

            return render(
                request, "registration/password_reset_confirm.html", {"validlink": True}
            )
        else:
            messages.error(request, "Liên kết không hợp lệ hoặc đã hết hạn")
            return redirect("login")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Liên kết không hợp lệ")
        return redirect("login")


class AdminOnlyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        data = [
            {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            }
            for user in users
        ]
        return Response({"users": data})


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    allowed_roles = ["user", "admin"]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_staff": user.is_staff,
            }
        )

    def put(self, request):
        user = request.user
        data = request.data
        if "email" in data:
            user.email = data["email"]

        user.save()
        return Response({"message": "Cập nhật thông tin thành công"})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def change_user_role(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        new_role = request.data.get("role")

        if new_role not in ["admin", "user"]:
            return Response(
                {"error": "Vai trò không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.role = new_role
        user.save()

        return Response(
            {"message": f"Đã thay đổi vai trò của {user.username} thành {new_role}"}
        )
    except User.DoesNotExist:
        return Response(
            {"error": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get("current_password")
    new_password = request.data.get("new_password")

    if not user.check_password(current_password):
        return Response(
            {"error": "Mật khẩu hiện tại không đúng"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(new_password) < 6:
        return Response(
            {"error": "Mật khẩu mới phải có ít nhất 6 ký tự"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save()

    return Response({"message": "Mật khẩu đã được thay đổi thành công"})


@login_required
@user_required
def readings_table_view(request):
    """View hiển thị bảng dữ liệu Reading"""
    readings = Reading.objects.order_by("-timestamp")
    context = {"readings": readings, "total_readings": readings.count()}
    return render(request, "monitoring/readings_table.html", context)


@api_view(["GET"])
@permission_classes([])  # Bỏ yêu cầu authentication
def latest_reading(request):
    reading = Reading.objects.order_by("-timestamp").first()
    if reading:
        data = {
            "ph": reading.ph,
            "ntu": reading.ntu,
            "tds": reading.tds,
            "timestamp": reading.timestamp,
        }
        return Response(data)
    return Response({"error": "No data"}, status=404)


@api_view(["POST"])
@permission_classes([])
def upload_reading(request):
    try:
        ph = float(request.POST.get("ph", 0))
        ntu = float(request.POST.get("ntu", 0))
        tds = float(request.POST.get("tds", 0))

        reading = Reading.objects.create(ph=ph, ntu=ntu, tds=tds)

        return Response({"message": "Data received successfully", "id": reading.pk})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([])
def health_check(request):
    """
    🩺 System Health Check
    Returns system status, database connectivity, and basic metrics
    """
    try:
        # Check database
        reading_count = Reading.objects.count()
        latest_reading = Reading.objects.order_by("-timestamp").first()

        # System info
        health_data = {
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "version": "1.0.0",
            "database": {
                "status": "connected",
                "total_readings": reading_count,
                "latest_reading": (
                    latest_reading.timestamp.isoformat() if latest_reading else None
                ),
            },
            "services": {
                "api": "running",
                "sensor_data": "active" if latest_reading else "inactive",
            },
        }

        return Response(health_data)
    except Exception as e:
        return Response(
            {
                "status": "unhealthy",
                "timestamp": timezone.now().isoformat(),
                "error": str(e),
            },
            status=503,
        )
