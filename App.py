from flask import Flask, request, abort
import json
from gevent.pywsgi import WSGIServer
from main import *
import traceback

app = Flask(__name__)

@app.route('/add_info', methods=['POST'])
def add_info():
    try:
        data_dic = eval(request.data)
        file_p = data_dic['file_path']
        pic_p = data_dic['pic_path']

        # get_text(file_p)
        add_text(pic_p, file_p)

        result_img_path = 'D:\work\add_info2pic' + pic_p + '_save'
        return json.dumps({'result_img': result_img_path})

    except:
        print(traceback.print_exc())
        return json.dumps({'error': '处理发生错误！'})


if __name__ == "__main__":
    # app.run()
    http_server = WSGIServer(('0.0.0.0', 9920), app)
    print('准备就绪')
    http_server.serve_forever()
