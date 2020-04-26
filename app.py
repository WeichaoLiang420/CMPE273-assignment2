from flask import Flask, escape, request
from flask import make_response
import sqlite3
import os
import json
import re


app = Flask(__name__)
stu_id = 1001


@app.before_first_request
def start_db():
  conn = sqlite3.connect('test.db')
  c = conn.cursor()
  
  c.execute("""CREATE TABLE IF NOT EXISTS subjects (
                                    c_id integer PRIMARY KEY,
                                    subject_name text,
                                    right_answers text
                                      )""")
  c.execute("""CREATE TABLE IF NOT EXISTS submission(
                                    s_id integer PRIMARY KEY, 
                                    id integer,
                                    subject_name text,
                                    student_name text,
                                    url text,
                                    score integer,
                                    input text,
                                    output text,
                                    foreign key(id) references subjects(c_id)
                                        )""")                                    
  conn.commit()
  conn.close()


@app.route('/api/tests',methods=['POST'])
def create_a_test():
     resjson = request.get_json()
     subject_name = resjson["subject_name"]
     right_answers = resjson["right_answers"]
    #  print(resjson) #{'subject_name': 'math', 'c_id': 1}
    #  print(subject_name) # math
     #print(c_id) #1
     conn = sqlite3.connect('test.db')
     c = conn.cursor()
     c.execute("INSERT INTO subjects(subject_name, right_answers) values ('{}','{}')".format(subject_name, right_answers))   
     handler = (subject_name,)
     c.execute("SELECT * FROM subjects WHERE subject_name=?",handler)
     conn.commit() 
     row=c.fetchone() 
     c_id = row[0]
     conn.close()
     return {"subject_name":subject_name,
     "c_id":c_id,
     "right_answers":right_answers,
     "submission":[ ]},201

@app.route('/api/tests/<c_id>/scantrons',methods=['POST'])
def create_a_upload(c_id):
     resjson = request.get_json()
     student_name=resjson["name"]
     subject_name = resjson["subject"]
     student_input = resjson["answers"]
     student_input1 = json.dumps(student_input)
    #  punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~" "'''
    #  no_punct = ""
    #  for char in student_input1:
    #    if char not in punctuations:
    #      no_punct = no_punct + char  
    #  remove_input = ''.join([i for i in no_punct if not i.isdigit()])
     conn = sqlite3.connect('test.db')
     c = conn.cursor()
     handler = (c_id,)
     c.execute("SELECT * FROM subjects WHERE c_id=?",handler) 
     conn.commit()
     row=c.fetchone() 
     right_answers = row[2] 
     dic = {}
     store = []
     store = right_answers.split(',')
     for i in range(len(store)):
       store[i]
       data = store[i]
       data = data.split(':')
       k=data[0]
       value = data[1]
       dic.update({k: value}) 
     print(dic)    
     count =100
     result = {}
     for key in student_input:
       if dic[key] !=student_input[key]:
         count-=2
       result[key] = {"atually":student_input[key],"expected":dic[key]}  
     url = "http://localhost:5000/files/scantron-"+c_id+".json"
     output = json.dumps(result)
     c.execute("""INSERT INTO submission(id,subject_name,student_name,url,input,score,output) values (?,?,?,?,?,?,?);""",(c_id,subject_name, student_name,url,student_input1,count,output)) 
    #  c.execute("INSERT INTO submission(id,subject_name,student_name,url,input,score,output) values ('{}','{}','{}','{}','{}','{}','{}')".format(c_id,subject_name,student_name,url,student_input,count,output))
     conn.commit()
     conn.close()

     return {"scantron_id":c_id,
     "name":student_name,
     "subject":subject_name,
     "score":count,
     "url":url,
     "result":result},201 






@app.route('/api/tests/<c_id>',methods=['GET'])
def check_scantrons(c_id):
  resjson = request.get_json()
  conn = sqlite3.connect('test.db')
  c = conn.cursor()
  handler = (c_id,)
  c.execute("SELECT * FROM subjects WHERE c_id=?",handler) 
  conn.commit()
  row=c.fetchone() 
  c_id = row[0]
  subject_name = [1]
  right_answers = row[2]
  handler = (c_id,)
  c.execute("SELECT * FROM submission WHERE id=?",handler)
  conn.commit()
  n=c.fetchall() 
  i=0
  arr_1=[]
  while i <len(n):
    s = n[i]
    i+=1
    scantron_id = s[0]
    c_id1 = s[1]
    subject_name1=s[2]
    student_name=s[3]
    url=s[4]
    score=s[5]
    student_input=s[6]
    output=s[7]
    arry=["scantro: ",scantron_id,"url: ",url,"name ",student_name,"subject: ", subject_name1,"score: ",score,"result: ",output]
    arr_1.append(arry)

  return {"test_id":c_id,
  "subject_name":subject_name,
  "answer_keys":right_answers,
  "submission ": arr_1}, 201
  


     
    



     









