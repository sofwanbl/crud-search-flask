from flask import render_template, request, url_for, redirect
from flaskext.mysql import MySQL
from app import app
from app.frm_entry import EntryForm

# Connecting database
app.config["MYSQL_DATABASE_HOST"]="localhost"
app.config["MYSQL_DATABASE_USER"]="root"
app.config["MYSQL_DATABASE_PASSWORD"]="your_database_password"
app.config["MYSQL_DATABASE_DB"]="your_database"
app.config["MYSQL_PORT"]="3306"

# Preparing variable on mysqlnya
mysqlnya=MySQL(app)
mysqlnya.init_app(app)

@app.route("/")
def home():
    return render_template("home.html", title="Home")


@app.route("/frm_entry", methods=["GET","POST"])
def frm_entry():
    resultnya=0
    rem=""
    xvalue_1=0
    xvalue_2=0
    xoperator=""    
    
    formnya=EntryForm()
    
    # Save inputted data to variables
    if request.method=="POST":
        details=request.form
        xvalue_1=details["value_1"]
        xvalue_2=details["value_2"]
        xoperator=details["operatornya"]
    
    # Processing result
    if xoperator=="+":
       resultnya=float(xvalue_1)+float(xvalue_2)
    elif xoperator=="-":
       resultnya=float(xvalue_1)-float(xvalue_2)
    elif xoperator=="/":
       resultnya=float(xvalue_1)/float(xvalue_2)
    elif xoperator=="*":
       resultnya=float(xvalue_1)*float(xvalue_2)    
   
    # Processing remarks, Even, Odd or Zero
    if resultnya==0:
        rem="Zero"
    elif resultnya % 2 ==0:    
        rem="Even"
    elif resultnya % 2==1:
         rem="Odd"    
    else:
        rem=""

    # Save data       
    if ( not (xvalue_1==0 and xvalue_2==0 and len(xoperator)==0) and not (len(xoperator)==0)):            
        cur=mysqlnya.connect().cursor()
        cur.execute("insert into penjumlahan (value_1,value_2,operator,result, remark) values (%s,%s,%s,%s,%s)",((xvalue_1,xvalue_2,xoperator,resultnya,rem)))
        cur.connection.commit()
        cur.close()   
      
    
    return render_template("frm_entry.html", title="Nilai", formnya=formnya, xresultnya=resultnya, remnya=rem)

@app.route("/display_data", methods=["GET","POST"])    
def display_data():
    formnya=EntryForm()     
    
    xvalue_1=0
    xvalue_2=0
    xoperator=""
    wherenya_1=""
    wherenya_2=""
    wherenya_3=""
    
    # Save inputted data to variables
    if request.method=="POST":
        details=request.form
        xvalue_1=details["value_1"]
        xvalue_2=details["value_2"]
        xoperator=details["operatornya"]
    
    # Search value 1
    if len(xvalue_1)>0:       
       wherenya_1=" where value_1="+xvalue_1
    else:      
       wherenya_1=""
    
    # Search value 2   
    if len(xvalue_1)>0:
      if len(xvalue_2)>0:              
          wherenya_2=" and value_2="+xvalue_2
    else:      
       if len(xvalue_2)>0:              
           wherenya_2=" where value_2="+xvalue_2
           
   # Search value 3           
    if len(xvalue_1)>0 or len(xvalue_2)>0:
      if len(xoperator)>0:              
        wherenya_3=" and operator="+ xoperator
    else:      
      if len(xoperator)>0:              
          wherenya_3=" where operator="+ xoperator       
           
    cur=mysqlnya.connect().cursor()    
    cur.execute("select * from penjumlahan "+ wherenya_1 + wherenya_2 + wherenya_3)
    hasilnya=cur.fetchall()    
    return render_template("tampil_data.html", title="Tampil Data",hasilnya=hasilnya,no=1,formnya=formnya)

@app.route("/frm_edit_data/<id>",methods=["GET","POST"])
def frm_edit_data(id):
    cur=mysqlnya.connect().cursor()
    form=EntryForm()
    cur.execute("select * from penjumlahan where id='"+id+"'")
    hasilnya=cur.fetchall()    
    for rows in hasilnya:
        xvalue_1=rows[1]
        xvalue_2=rows[2]
        xoperator=rows[3]
        xresult=rows[4]
        xremark=rows[5]    
        
    if request.method=="POST":       
       
       details=request.form
       xvalue_1=details["value_1"]
       xvalue_2=details["value_2"]
       xoperator=details["operatornya"]
       
       # Memproses hasil    
       if xoperator=="+":
          xresult=float(xvalue_1)+float(xvalue_2)
       elif xoperator=="-":
          xresult=float(xvalue_1)-float(xvalue_2)
       elif xoperator=="/":
          xresult=float(xvalue_1)/float(xvalue_2)
       elif xoperator=="*":
           xresult=float(xvalue_1)*float(xvalue_2)
       else:
           xresult=0
        
       # Menentukan Ganjil atau Genap
       if xresult % 2 ==0:
          xremark="Even"
       elif xresult % 2==1:
          xremark="Odd"
       else:
          xremark="Zero"   
       
       cur=mysqlnya.connect().cursor()
       #cur.execute("update penjumlahan set value_1='"+xnilai_1+"'"+
       #            ",value_2='"+xnilai_2+"'"+",operator='"+xoperator+"'"+
       #            ",result='"+hasil+"'"+",remark='"+xremark+"'"+"where id='"+id+"'")
       
       cur.execute ("update penjumlahan set value_1=%s,value_2=%s,operator=%s,result=%s,remark=%s where id= %s",
                    ((xvalue_1,xvalue_2,xoperator,xresult,xremark,id)))
       cur.connection.commit()
       cur.close()
    else:   
       form.value_1.data=xvalue_1    
       form.value_2.data=xvalue_2
       form.operatornya.data=xoperator          
    
    return render_template("frm_edit.html", title="Edit Data",znilai_1=xvalue_1,form=form,
                           ketnya=xremark,hasilnya=xresult)    

@app.route("/delete_data/<id>", methods=["GET","POST"])
def delete_data(id):
    cur=mysqlnya.connect().cursor()
    cur.execute("delete from penjumlahan where id='"+id+"'")
    cur.connection.commit()
    cur.close()    
    return redirect(url_for("display_data"))
