from gevent import monkey
monkey.patch_all()
from flask import Flask, send_from_directory
from flask_socketio import SocketIO # 1. 소켓 라이브러리 임포트 확인!
from memberA import bp_a
from memberB import bp_b
from memberC import bp_c
from memberD import bp_d

app = Flask(__name__, static_folder="static", template_folder="static")
# async_mode='gevent'를 꼭 명시해 줍니다.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')
app.register_blueprint(bp_a)
app.register_blueprint(bp_b)
app.register_blueprint(bp_c)
app.register_blueprint(bp_d)

@app.route("/")
def index(): return send_from_directory("static", "index.html")



if __name__ == "__main__":
    print("반려동물 건강 가이드 통합 서버 가동 성공!")
    print("http://127.0.0.1:5002")

    socketio.run(app, debug=True, port=5002)
