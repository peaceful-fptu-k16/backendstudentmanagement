"""
Generate Beautiful Sample Students Data
Creates 100 realistic Vietnamese student records
"""

import json
import random
from datetime import date, timedelta

# Vietnamese first names (diverse and realistic)
first_names_male = [
    "Minh", "Hoàng", "Nam", "Hải", "Khoa", "Duy", "Phúc", "Tùng", "Thành", "Quân",
    "Hưng", "Tuấn", "Đức", "Thiện", "Long", "Cường", "Bình", "An", "Trí", "Kiên",
    "Tân", "Hùng", "Vũ", "Lâm", "Đạt", "Huy", "Phong", "Anh", "Sơn", "Toàn"
]

first_names_female = [
    "Linh", "Hương", "Lan", "Mai", "Thu", "Hà", "Trang", "Ngọc", "Phương", "Thảo",
    "Huyền", "Nhung", "Vy", "Chi", "My", "Như", "Giang", "Diệu", "Thanh", "Quỳnh",
    "Ánh", "Yến", "Trâm", "Châu", "Khánh", "Tú", "Hạnh", "Dung", "Loan", "Thư"
]

# Vietnamese last names (most common)
last_names = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Võ", "Đặng", "Bùi",
    "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Đào", "Lưu", "Trương", "Tạ",
    "Huỳnh", "Mai", "Tô", "Lâm", "Trịnh", "Hà", "Tăng", "Cao", "Phan", "Chu"
]

# Vietnamese provinces/cities (63 tỉnh thành)
hometowns = [
    "Hà Nội", "TP.HCM", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
    "Hải Dương", "Hưng Yên", "Nam Định", "Thái Bình", "Ninh Bình",
    "Thanh Hóa", "Nghệ An", "Hà Tĩnh", "Quảng Bình", "Quảng Trị",
    "Thừa Thiên Huế", "Quảng Nam", "Quảng Ngãi", "Bình Định", "Phú Yên",
    "Khánh Hòa", "Ninh Thuận", "Bình Thuận", "Kon Tum", "Gia Lai",
    "Đắk Lắk", "Đắk Nông", "Lâm Đồng", "Bình Phước", "Tây Ninh",
    "Bình Dương", "Đồng Nai", "Bà Rịa - Vũng Tàu", "Long An", "Tiền Giang",
    "Bến Tre", "Trà Vinh", "Vĩnh Long", "Đồng Tháp", "An Giang",
    "Kiên Giang", "Cà Mau", "Bạc Liêu", "Sóc Trăng", "Hậu Giang",
    "Vĩnh Phúc", "Bắc Ninh", "Quảng Ninh", "Lạng Sơn", "Cao Bằng",
    "Bắc Kạn", "Thái Nguyên", "Yên Bái", "Tuyên Quang", "Hà Giang",
    "Điện Biên", "Lai Châu", "Sơn La", "Hòa Bình", "Phú Thọ",
    "Lào Cai", "Bắc Giang", "Thái Bình"
]

def generate_score():
    """Generate realistic score with distribution"""
    # 10% Excellent (9.0-10.0)
    # 30% Good (8.0-8.9)
    # 40% Average (6.5-7.9)
    # 15% Below Average (5.0-6.4)
    # 5% Poor (0-4.9)
    
    rand = random.random()
    if rand < 0.10:  # Excellent
        return round(random.uniform(9.0, 10.0), 2)
    elif rand < 0.40:  # Good
        return round(random.uniform(8.0, 8.9), 2)
    elif rand < 0.80:  # Average
        return round(random.uniform(6.5, 7.9), 2)
    elif rand < 0.95:  # Below Average
        return round(random.uniform(5.0, 6.4), 2)
    else:  # Poor
        return round(random.uniform(3.0, 4.9), 2)

def generate_birth_date():
    """Generate birth date between 2002-2005"""
    start_date = date(2002, 1, 1)
    end_date = date(2005, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return (start_date + timedelta(days=random_days)).isoformat()

def remove_vietnamese_accents(text):
    """Remove Vietnamese accents from text"""
    accents = {
        'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    }
    result = text.lower()
    for viet, eng in accents.items():
        result = result.replace(viet, eng)
    return result

def generate_students(count=100):
    """Generate beautiful student data"""
    students = []
    used_ids = set()
    
    for i in range(count):
        # Generate unique ID
        student_id = f"SV{str(i+1).zfill(4)}"
        
        # Random gender for name selection
        is_male = random.choice([True, False])
        first_name = random.choice(first_names_male if is_male else first_names_female)
        last_name = random.choice(last_names)
        
        # Create email: firstname+lastname+studentid (no dots, no accents)
        # Example: thulyse0001@university.edu.vn
        first_no_accent = remove_vietnamese_accents(first_name)
        last_no_accent = remove_vietnamese_accents(last_name)
        email_name = f"{first_no_accent}{last_no_accent}{student_id.lower()}"
        
        email = f"{email_name}@university.edu.vn"
        
        # Generate scores with some correlation
        base_ability = random.uniform(5.5, 9.0)
        math_score = max(0, min(10, generate_score() * 0.7 + base_ability * 0.3))
        literature_score = max(0, min(10, generate_score() * 0.7 + base_ability * 0.3))
        english_score = max(0, min(10, generate_score() * 0.7 + base_ability * 0.3))
        
        # Round to 1 decimal
        math_score = round(math_score, 1)
        literature_score = round(literature_score, 1)
        english_score = round(english_score, 1)
        
        student = {
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "birth_date": generate_birth_date(),
            "hometown": random.choice(hometowns),
            "math_score": math_score,
            "literature_score": literature_score,
            "english_score": english_score
        }
        
        students.append(student)
    
    return students

def main():
    """Generate and save beautiful student data"""
    print("🎨 Generating beautiful student data...")
    
    students = generate_students(100)
    
    # Sort by student_id for consistency
    students.sort(key=lambda x: x['student_id'])
    
    # Save to file
    output_file = "data/sample_students_100.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(students, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated {len(students)} students")
    print(f"📁 Saved to: {output_file}")
    
    # Show statistics
    print("\n📊 Statistics:")
    
    # Score distribution
    all_scores = []
    for s in students:
        all_scores.extend([s['math_score'], s['literature_score'], s['english_score']])
    
    excellent = sum(1 for score in all_scores if score >= 9.0)
    good = sum(1 for score in all_scores if 8.0 <= score < 9.0)
    average = sum(1 for score in all_scores if 6.5 <= score < 8.0)
    below_avg = sum(1 for score in all_scores if 5.0 <= score < 6.5)
    poor = sum(1 for score in all_scores if score < 5.0)
    
    total_scores = len(all_scores)
    print(f"   Excellent (9.0+): {excellent} ({excellent/total_scores*100:.1f}%)")
    print(f"   Good (8.0-8.9): {good} ({good/total_scores*100:.1f}%)")
    print(f"   Average (6.5-7.9): {average} ({average/total_scores*100:.1f}%)")
    print(f"   Below Avg (5.0-6.4): {below_avg} ({below_avg/total_scores*100:.1f}%)")
    print(f"   Poor (<5.0): {poor} ({poor/total_scores*100:.1f}%)")
    
    # Hometown distribution
    from collections import Counter
    hometown_counts = Counter(s['hometown'] for s in students)
    print(f"\n🌍 Top 5 Hometowns:")
    for hometown, count in hometown_counts.most_common(5):
        print(f"   {hometown}: {count} students")
    
    # Show sample
    print("\n📋 Sample (first 3 students):")
    for student in students[:3]:
        avg = (student['math_score'] + student['literature_score'] + student['english_score']) / 3
        print(f"\n   {student['student_id']} - {student['first_name']} {student['last_name']}")
        print(f"   Email: {student['email']}")
        print(f"   Hometown: {student['hometown']}")
        print(f"   Scores: {student['math_score']} | {student['literature_score']} | {student['english_score']} (Avg: {avg:.2f})")

if __name__ == "__main__":
    main()
