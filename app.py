from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

EXCEL_FILE = '2029دفعة.xlsx'

def load_data():
    return pd.read_excel(EXCEL_FILE, header=None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('student_id')
    query_str = str(query).strip()
    df = load_data()
    # البحث في الأعمدة: 0 (جامعي)، 1 (امتحاني)، 5 (اسم)، 4 (تحضيرية)
    mask = (df[0].astype(str) == query_str) | \
           (df[1].astype(str) == query_str) | \
           (df[5].astype(str) == query_str) | \
           (df[4].astype(str) == query_str)
    
    student_row = df[mask]
    if not student_row.empty:
        # نمرر رقم السطر index ومصفوفة الطالب s
        student_index = student_row.index[0]
        return render_template('student.html', s=student_row.iloc[0].tolist(), student_index=student_index)
    return "<h3>الطالب غير موجود</h3><a href='/'>رجوع</a>"

@app.route('/sort', methods=['POST'])
def sort_students():
    try:
        col_index = int(request.form.get('column_index'))
        df = load_data()
        # تحويل العمود لأرقام للفرز الصحيح
        df[col_index] = pd.to_numeric(df[col_index], errors='coerce')
        df_sorted = df.dropna(subset=[col_index]).sort_values(by=col_index, ascending=False)
        
        # نرسل النتيجة مع الـ index الخاص بكل طالب
        results = []
        for idx, row in df_sorted.iterrows():
            results.append({'index': idx, 'data': row.tolist()})
            
        return render_template('index.html', results=results, sorted_col=col_index)
    except Exception as e:
        return f"خطأ تقني: {e}"

@app.route('/student/<student_id>')
def student_details(student_id):
    df = load_data()
    student_row = df[df[0].astype(str) == str(student_id)]
    if not student_row.empty:
        student_index = student_row.index[0]
        return render_template('student.html', s=student_row.iloc[0].tolist(), student_index=student_index)
    return "<h3>بيانات الطالب غير موجودة</h3><a href='/'>رجوع</a>"

# مسار كشف العلامات الرسمي (تم نقله قبل تشغيل التشغيل الرئيسي)
@app.route('/transcript/<int:student_index>')
def get_transcript(student_index):
    try:
        df = load_data()
        student_row = df.iloc[student_index].values  
        return render_template('transcript.html', row=student_row)
    except Exception as e:
        return f"<h3>حدث خطأ في تحميل الكشف: {e}</h3><a href='/'>رجوع</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
