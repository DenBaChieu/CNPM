import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

print("\n" + "=" * 70)
print("TEST CẤU HÌNH BIỂU PHÍ (UC06)")
print("=" * 70)

# Bước 1: Đăng nhập
print("\n" + "=" * 70)
print("BƯỚC 1: Đăng nhập lấy token admin")
print("=" * 70)

login_response = requests.post(
    f"{BASE_URL}/login",
    json={"id": 0, "password": "Admin"}
)
print(f"Status: {login_response.status_code}")
print(f"Response: {json.dumps(login_response.json(), indent=2)}")

if login_response.status_code != 200:
    print("\n❌ LỖI: Không thể đăng nhập. Kiểm tra xem backend có chạy không?")
    exit()

token = login_response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"\n✅ Token lấy được: {token[:50]}...")

# Bước 2: Tạo biểu phí cho Student
print("\n" + "=" * 70)
print("BƯỚC 2: Tạo biểu phí cho Student (hourly, 1000/giờ)")
print("=" * 70)

policy_student = {
    "groupTarget": "Student",
    "priceType": "hourly",
    "priceValue": 1000,
    "startDate": "2024-01-01T00:00:00",
    "endDate": "2024-12-31T23:59:59",
    "isActive": True
}

print(f"Input: {json.dumps(policy_student, indent=2)}")
response = requests.post(
    f"{BASE_URL}/billing/policy",
    json=policy_student,
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("✅ Tạo policy Student thành công")
    student_policy_id = response.json().get("policyId")
else:
    print("❌ Lỗi khi tạo policy Student")

# Bước 3: Tạo biểu phí cho Visitor
print("\n" + "=" * 70)
print("BƯỚC 3: Tạo biểu phí cho Visitor (per_turn, 5000/lần)")
print("=" * 70)

policy_visitor = {
    "groupTarget": "Visitor",
    "priceType": "per_turn",
    "priceValue": 5000,
    "startDate": "2024-01-01T00:00:00",
    "endDate": "2024-12-31T23:59:59",
    "isActive": True
}

print(f"Input: {json.dumps(policy_visitor, indent=2)}")
response = requests.post(
    f"{BASE_URL}/billing/policy",
    json=policy_visitor,
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("✅ Tạo policy Visitor thành công")
    visitor_policy_id = response.json().get("policyId")
else:
    print("❌ Lỗi khi tạo policy Visitor")

# Bước 4: Tạo thêm biểu phí cho Staff
print("\n" + "=" * 70)
print("BƯỚC 4: Tạo biểu phí cho Staff (hourly, 500/giờ - giảm giá)")
print("=" * 70)

policy_staff = {
    "groupTarget": "Staff",
    "priceType": "hourly",
    "priceValue": 500,
    "startDate": "2024-01-01T00:00:00",
    "endDate": "2024-12-31T23:59:59",
    "isActive": True
}

print(f"Input: {json.dumps(policy_staff, indent=2)}")
response = requests.post(
    f"{BASE_URL}/billing/policy",
    json=policy_staff,
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("✅ Tạo policy Staff thành công")
else:
    print("❌ Lỗi khi tạo policy Staff")

# Bước 5: Xem tất cả biểu phí
print("\n" + "=" * 70)
print("BƯỚC 5: Xem tất cả biểu phí đã tạo")
print("=" * 70)

response = requests.get(
    f"{BASE_URL}/billing/policy",
    headers=headers
)
print(f"Status: {response.status_code}")
policies = response.json().get("policies", [])
print(f"Tổng số policy: {len(policies)}")
for idx, policy in enumerate(policies, 1):
    print(f"\n  Policy #{idx}:")
    print(f"    - ID: {policy.get('policyId')[:20]}...")
    print(f"    - Nhóm: {policy.get('groupTarget')}")
    print(f"    - Loại phí: {policy.get('priceType')}")
    print(f"    - Giá: {policy.get('priceValue')} VND")
    print(f"    - Từ: {policy.get('startDate')}")
    print(f"    - Đến: {policy.get('endDate')}")
    print(f"    - Trạng thái: {'Hoạt động' if policy.get('isActive') else 'Tắt'}")

if len(policies) >= 3:
    print("\n✅ Tất cả 3 policy đã được tạo thành công")
else:
    print(f"\n❌ Chỉ có {len(policies)} policy, cần 3 cái")

# Bước 6: Xem chu kỳ thanh toán (trước)
print("\n" + "=" * 70)
print("BƯỚC 6: Xem chu kỳ thanh toán (TRƯỚC khi bắt đầu)")
print("=" * 70)

response = requests.get(
    f"{BASE_URL}/billing/period",
    headers=headers
)
print(f"Status: {response.status_code}")
period_data = response.json()
print(f"Start Time: {period_data.get('startTime')}")
print(f"End Time: {period_data.get('endTime')}")

if period_data.get('startTime') is None:
    print("✅ Chu kỳ chưa bắt đầu (như mong đợi)")
else:
    print("⚠️ Chu kỳ đã bắt đầu trước đó")

# Bước 7: Bắt đầu chu kỳ thanh toán
print("\n" + "=" * 70)
print("BƯỚC 7: Bắt đầu chu kỳ thanh toán")
print("=" * 70)

response = requests.post(
    f"{BASE_URL}/payment/startBillingPeriod",
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("✅ Chu kỳ thanh toán đã bắt đầu")
else:
    print("❌ Lỗi khi bắt đầu chu kỳ")

# Bước 8: Xem chu kỳ (sau bắt đầu)
print("\n" + "=" * 70)
print("BƯỚC 8: Xem chu kỳ thanh toán (SAU khi bắt đầu)")
print("=" * 70)

response = requests.get(
    f"{BASE_URL}/billing/period",
    headers=headers
)
print(f"Status: {response.status_code}")
period_data = response.json()
print(f"Start Time: {period_data.get('startTime')}")
print(f"End Time: {period_data.get('endTime')}")

if period_data.get('startTime') is not None and period_data.get('endTime') is None:
    print("✅ Chu kỳ đã bắt đầu và chưa kết thúc (như mong đợi)")
    start_time = period_data.get('startTime')
else:
    print("❌ Trạng thái chu kỳ không đúng")

# Bước 9: Cập nhật biểu phí (thay đổi giá)
print("\n" + "=" * 70)
print("BƯỚC 9: Cập nhật biểu phí (tăng giá Student lên 1500/giờ)")
print("=" * 70)

updated_policy = {
    "policyId": student_policy_id,
    "groupTarget": "Student",
    "priceType": "hourly",
    "priceValue": 1500,  # Tăng từ 1000 lên 1500
    "startDate": "2024-01-01T00:00:00",
    "endDate": "2024-12-31T23:59:59",
    "isActive": True
}

print(f"Input: {json.dumps(updated_policy, indent=2)}")
response = requests.post(
    f"{BASE_URL}/billing/policy",
    json=updated_policy,
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("✅ Cập nhật policy Student thành công")
else:
    print("❌ Lỗi khi cập nhật policy")

# Bước 10: Xem lại danh sách policy (sau cập nhật)
print("\n" + "=" * 70)
print("BƯỚC 10: Xem lại danh sách policy (sau cập nhật)")
print("=" * 70)

response = requests.get(
    f"{BASE_URL}/billing/policy",
    headers=headers
)
print(f"Status: {response.status_code}")
policies = response.json().get("policies", [])

for policy in policies:
    if policy.get('groupTarget') == 'Student':
        print(f"Policy Student:")
        print(f"  - Loại phí: {policy.get('priceType')}")
        print(f"  - Giá: {policy.get('priceValue')} VND (cần là 1500)")
        if policy.get('priceValue') == 1500:
            print("  ✅ Giá đã được cập nhật đúng")
        else:
            print(f"  ❌ Giá không đúng (hiện là {policy.get('priceValue')})")

# Bước 11: Kết thúc chu kỳ thanh toán
print("\n" + "=" * 70)
print("BƯỚC 11: Kết thúc chu kỳ thanh toán")
print("=" * 70)

response = requests.post(
    f"{BASE_URL}/payment/stopBillingPeriod",
    headers=headers
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("✅ Chu kỳ thanh toán đã kết thúc")
else:
    print("❌ Lỗi khi kết thúc chu kỳ")

# Bước 12: Xem chu kỳ (sau kết thúc)
print("\n" + "=" * 70)
print("BƯỚC 12: Xem chu kỳ thanh toán (SAU khi kết thúc)")
print("=" * 70)

response = requests.get(
    f"{BASE_URL}/billing/period",
    headers=headers
)
print(f"Status: {response.status_code}")
period_data = response.json()
print(f"Start Time: {period_data.get('startTime')}")
print(f"End Time: {period_data.get('endTime')}")

if period_data.get('startTime') is not None and period_data.get('endTime') is not None:
    print("✅ Chu kỳ đã bắt đầu và kết thúc (như mong đợi)")
    end_time = period_data.get('endTime')
    print(f"Thời gian chạy: từ {start_time} đến {end_time}")
else:
    print("❌ Trạng thái chu kỳ không đúng")

# Test lỗi: Token không hợp lệ
print("\n" + "=" * 70)
print("BƯỚC 13: TEST LỖI - Gọi API với token sai")
print("=" * 70)

bad_headers = {"Authorization": "Bearer INVALID_TOKEN_123"}
response = requests.get(
    f"{BASE_URL}/billing/policy",
    headers=bad_headers
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 401:
    print("✅ Hệ thống đúng cách từ chối token không hợp lệ")
else:
    print("❌ Hệ thống không kiểm tra token đúng cách")

# Tóm tắt
print("\n" + "=" * 70)
print("TÓM TẮT KẾT QUẢ TEST")
print("=" * 70)
print("""
✅ Test tạo biểu phí (Student, Visitor, Staff)
✅ Test xem danh sách biểu phí
✅ Test bắt đầu chu kỳ thanh toán
✅ Test cập nhật biểu phí
✅ Test kết thúc chu kỳ thanh toán
✅ Test bảo mật (token không hợp lệ)

Nếu tất cả đều ✅ thì backend UC06 hoạt động đúng!
""")
print("=" * 70 + "\n")
