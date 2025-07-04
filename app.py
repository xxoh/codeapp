import streamlit as st
from datetime import datetime
import qrcode
from io import BytesIO
import base64
from math import gcd
import random

# RSA 관련 함수 정의
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

# RSA 키 유지
if "rsa_keys" not in st.session_state:
    st.session_state.rsa_keys = choose_keys()
e, d, n = st.session_state.rsa_keys

# 출석 상태 유지
if "present_list" not in st.session_state:
    st.session_state.present_list = []
if "encrypted_data" not in st.session_state:
    st.session_state.encrypted_data = []

# 학급 명단
class_list = [str(i) for i in range(30901, 30921)]

# UI
st.title("📚 RSA 기반 QR 출석 시스템")
st.write("### 👩‍🎓 학생 출석 입력")
student_id = st.text_input("학번 입력 (30901~30920):")

if st.button("출석하기"):
    if student_id not in class_list:
        st.warning("❌ 명단에 없는 학번입니다.")
    elif student_id in st.session_state.present_list:
        st.warning("⚠️ 이미 출석한 학생입니다.")
    else:
        now = datetime.now().strftime("%H:%M:%S")
        message = f"{student_id}_{now}"
        cipher = encrypt(message, e, n)
        st.session_state.encrypted_data.append(cipher)
        st.session_state.present_list.append(student_id)

        # QR 코드 생성
        qr = qrcode.make(str(cipher))
        buf = BytesIO()
        qr.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.success(f"✅ 출석 완료! 도착 시간: {now}")
        st.image(byte_im, caption=f"학번 {student_id} QR코드", use_column_width=False)

# 명단 출력 버튼들
if st.button("출석 명단 보기"):
    st.subheader("📋 출석 명단")
    for i, cipher in enumerate(st.session_state.encrypted_data):
        try:
            decrypted = decrypt(cipher, d, n)
            sid, t = decrypted.split("_")
            st.write(f"{i+1}. 학번: {sid} / 도착 시간: {t}")
        except:
            st.write("⚠️ 복호화 실패")

if st.button("결석자 확인"):
    st.subheader("🚫 결석자 명단")
    absent_list = sorted(set(class_list) - set(st.session_state.present_list))
    if absent_list:
        for i, sid in enumerate(absent_list):
            st.write(f"{i+1}. 학번: {sid}")
    else:
        st.success("🎉 전원 출석!")
