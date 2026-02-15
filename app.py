from flask import Flask, render_template, request, redirect
import sqlite3
import numpy as np # For mathemetical operations
from sklearn.linear_model import LinearRegression # AI model 

app = Flask(__name__)

def pulldata():
    # If use with you do not need use dbconnection.close() method it is goning to close itself
    with sqlite3.connect("database.db") as dbconnection:
        cursor = dbconnection.cursor()
        cursor.execute("SELECT * FROM spends")
        data = cursor.fetchall()
    return data 

def ai_results(spends):
    category = {}
    forecasts = {}

    for s in spends:
        id , c , amount = s[0], s[1], s[2]
        if c not in category:
            category[c] = []
        category[c].append((id,amount))

    for c, spends in category.items():
        if len(spends) < 2 :
            forecasts[c] = "Enough data is not exist"
            continue

        X = np.array([s[0] for s in spends]).reshape(-1,1)
        y = np.array([s[1] for s in spends])

        model  = LinearRegression()
        model.fit(X,y)

        next_id  = np.array([[X[-1][0] + 1]])
        forecast = model.predict(next_id)
        forecasts[c] = f"{round(forecast[0],2)} TL"

    return forecasts


@app.route('/')
def main_page():
    spends = pulldata()
    predict_dictionary = ai_results(spends)

    total_spends = sum(s[2] for s in spends) if spends else 0 

    return render_template('index.html', spends=spends , predicts=predict_dictionary , total= total_spends )   


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