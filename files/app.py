from flask import Flask, request, jsonify, send_file, render_template
import csv
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# 配置信息
DOWNLOAD_FILE = 'ClusterSymPoly_250730Version.zip'  # 要下载的文件路径
RECORDS_FILE = 'downloads.csv'  # 下载记录文件

# 确保记录文件存在
if not os.path.exists(RECORDS_FILE):
    with open(RECORDS_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'email', 'timestamp'])

@app.route('/')
def index():
    # 计算下载次数
    download_count = 0
    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            download_count = sum(1 for row in reader) - 1  # 减去标题行
    
    return render_template('download.html', download_count=download_count)

@app.route('/record-download', methods=['POST'])
def record_download():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({'success': False, 'message': '姓名和邮箱不能为空'}), 400
        
        # 记录下载信息
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(RECORDS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([name, email, timestamp])
        
        # 计算新的下载次数
        download_count = 0
        if os.path.exists(RECORDS_FILE):
            with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                download_count = sum(1 for row in reader) - 1  # 减去标题行
        
        return jsonify({
            'success': True,
            'download_url': '/download-file',
            'downloadCount': download_count
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/download-file')
def download_file():
    # 提供文件下载
    return send_file(
        DOWNLOAD_FILE,
        as_attachment=True,
        download_name='ClusterSymPoly_250730Version.zip'
    )

@app.route('/view-records')
def view_records():
    # 这个路由仅供管理员查看下载记录（在实际应用中应添加身份验证）
    if not os.path.exists(RECORDS_FILE):
        return "暂无下载记录"
    
    records = []
    with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    # 按时间倒序排列
    records.reverse()
    
    html = """
    <html>
    <head>
        <title>下载记录</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
            tr:hover { background-color: #f5f5f5; }
        </style>
    </head>
    <body>
        <h1>文件下载记录</h1>
        <table>
            <tr>
                <th>姓名</th>
                <th>邮箱</th>
                <th>下载时间</th>
            </tr>
    """
    
    for record in records:
        html += f"""
            <tr>
                <td>{record['name']}</td>
                <td>{record['email']}</td>
                <td>{record['timestamp']}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
