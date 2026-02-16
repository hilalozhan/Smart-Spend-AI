from flask import Flask, render_template, request, redirect
import sqlite3
import numpy as np # For mathemetical operations
from sklearn.linear_model import LinearRegression # AI model 
from sklearn.metrics import r2_score 

app = Flask(__name__)

'''
## If want to start with an empty database we use this function 
def init_db():
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL
            )
        """)
    db.commit()

init_db()
'''


def pulldata():
    # If use with you do not need use dbconnection.close() method it is goning to close itself
    with sqlite3.connect("database.db") as dbconnection:
        cursor = dbconnection.cursor()
        cursor.execute("SELECT * FROM spends")
        data = cursor.fetchall()
    return data 

@app.route('/analysis')
def analysis_page():
    spends = pulldata()
    category_data = {}
    analysis_results = []

    # Gruping data into catories
    for s in spends:
        cid , cname, amount = s[0] , s[1] ,s[2] 
        if cname not in category_data:
             category_data[cname] = {'ids':[], 'amounts':[]}
        category_data[cname]['ids'].append(cid)
        category_data[cname]['amounts'] .append(amount)

    for cname , data in category_data.items():
        if len(data['amounts']) < 3 :
            continue
        
        X = np.array(data['ids']).reshape(-1,1)
        y = np.array(data['amounts'])

        model = LinearRegression()
        model.fit(X,y)

        # Model Accuracy (r2 score)
        y_pred = model.predict(X)
        accuracy = r2_score(y,y_pred) 

        # Future Predict
        next_id = np.array([[X[-1][0] + 1]])
        prediction = model.predict(next_id)[0] 

        analysis_results.append({
            'category': cname,
            'prediction': round(prediction, 2),
            'accuracy': round(accuracy * 100, 2), # % cinsinden
            'history_labels': data['ids'],
            'history_values': data['amounts'],
            'trend_line': [round(i, 2) for i in y_pred]
        })

    return render_template('analysis.html', results=analysis_results)


@app.route('/')
def main_page():
    spends = pulldata()
    total_spends = sum(s[2] for s in spends) if spends else 0 
    return render_template('index.html', spends=spends , total= total_spends )   



@app.route('/add', methods=['POST'])  # Added new path for take user data with POST method 
def add_spends():
    # Get data from form
    category = request.form.get('category')
    amount = request.form.get('amount')
    
    # Added new data db
    if category and amount: # This eliminate empty data attempt
        dbconnection = sqlite3.connect("database.db")
        cursor =dbconnection.cursor()
        cursor.execute("INSERT INTO spends(category,amount) VALUES (?,?)", (category,amount))
        dbconnection.commit()
        dbconnection.close()

    return redirect('/') # return main page 

@app.route('/delete/<int:id>')
def delete_spends(id):
    with sqlite3.connect('database.db') as dbconnection:
        cursor = dbconnection.cursor()
        cursor.execute('DELETE FROM spends WHERE id = ?', (id,)) 
        dbconnection.commit()
    return redirect('/')   

@app.route('/edit/<int:id>' , methods= ['POST'])
def edit_spends(id):
    if request.method == 'POST':
        category = request.form.get('category')
        amount = request.form.get('amount')
        with sqlite3.connect('database.db') as dbconnection:
            cursor = dbconnection.cursor()
            cursor.execute('UPDATE spends SET category=?, amount=?  WHERE id=?',(category,amount,id))   
        return redirect('/') 


#Starts server
if __name__ == '__main__':
    app.run(debug=True)