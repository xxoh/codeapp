import streamlit as st
from datetime import datetime
import qrcode
from io import BytesIO
import base64
from math import gcd
import random
import os

# RSA 함수
def str_to_int(message):
    return int.from_bytes(message.encode('utf-8'), byteorder='big')

def int_to_str(number):
    return number.to_bytes((number.bit_length() + 7) // 8, byteorder='big').decode('utf-8')

def encrypt(message, e, n):
    m = str_to_int(message)
    return pow(m, e, n)

def decrypt(cipher, d, n):
    m = pow(cipher, d, n)
    return int_to_str(m)

def choose_keys():
    p = 61
    q = 53
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = random.randint(2, phi_n - 1)
    while gcd(e, phi_n) != 1:
        e = random.randint(2, phi_n - 1)
    def extended_gcd(a, b):
        if b == 0:
            return (1, 0)
        else:
            x1, y1 = extended_gcd(b, a % b)
            x = y1
            y = x1 - (a // b) * y1
            return (x, y)
    def modinv(e, phi):
        x, _ = extended_gcd(e, phi)
        return x % phi
    d = modinv(e, phi_n)
    return e, d, n

# 고정된 RSA 키 사용 (클라우드에서도 동일하게 되도록)
e = 17
d = 2753
n = 3233

# 명단
class_list = [str(i) for i in range(30901, 30921)]
attend_file = "attend.txt"

# Streamlit UI
st.title("📚 RSA 기반 QR 출석 시스템")
st.write("### 👩‍🎓 학생 출석 입력")
student_id = st.text_input("학번 입력 (30901~30920):")

# 출석 처리
if st.button("출석하기"):
    if student_id not in class_list:
        st.warning("❌ 명단에 없는 학번입니다.")
    else:
        if os.path.exists(attend_file):
            with open(attend_file, "r") as f:
                existing = f.read().splitlines()
        else:
            existing = []

        if student_id in [decrypt(int(line), d, n).split("_")[0] for line in existing]:
            st.warning("⚠️ 이미 출석한 학생입니다.")
        else:
            now = datetime.now().strftime("%H:%M:%S")
            message = f"{student_id}_{now}"
            cipher = encrypt(message, e, n)

            with open(attend_file, "a") as f:
                f.write(f"{cipher}\n")

            qr = qrcode.make(str(cipher))
            buf = BytesIO()
            qr.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.success(f"✅ 출석 완료! 도착 시간: {now}")
            st.image(byte_im, caption=f"학번 {student_id} QR코드", use_column_width=False)

# 출석 명단 보기
if st.button("출석 명단 보기"):
    st.subheader("📋 출석 명단")
    if os.path.exists(attend_file):
        with open(attend_file, "r") as f:
            lines = f.read().splitlines()
        for i, line in enumerate(lines):
            try:
                decrypted = decrypt(int(line), d, n)
                sid, t = decrypted.split("_")
                st.write(f"{i+1}. 학번: {sid} / 도착 시간: {t}")
            except:
                st.write("⚠️ 복호화 실패")
    else:
        st.info("아직 아무도 출석하지 않았습니다.")

# 결석자 명단
if st.button("결석자 확인"):
    st.subheader("🚫 결석자 명단")
    if os.path.exists(attend_file):
        with open(attend_file, "r") as f:
            lines = f.read().splitlines()
        present_list = [decrypt(int(line), d, n).split("_")[0] for line in lines]
    else:
        present_list = []

    absent_list = sorted(set(class_list) - set(present_list))
    if absent_list:
        for i, sid in enumerate(absent_list):
            st.write(f"{i+1}. 학번: {sid}")
    else:
        st.success("🎉 전원 출석!")
