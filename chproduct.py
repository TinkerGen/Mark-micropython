

# from elfbotnodesenabler import *
import os
import machine

# user_event_tasks = []
# MAX_EVENT_TASK_COUNT = 11

def registe_event_task(event_task):
  global user_event_tasks
  global MAX_EVENT_TASK_COUNT
  if len(user_event_tasks) < MAX_EVENT_TASK_COUNT:
    user_event_tasks.append(event_task)
    event_task.start()
    
def product_name():
  productname = ''
  try:
    f = open('productname.txt', 'r')
    productname = f.read()
    f.close()
  except:
    pass
  return productname
  
def product_version():
  productver = ''
  try:
    f = open('productnameversion.txt', 'r')
    productver = f.read()
    f.close()
  except:
    pass
  return productver
"""  
def stop_user_tasks():
  global enabler
  #停止事件分发
  enabler.stop_event_dispatch()
  
  global user_event_tasks
  #停止所有的用户EVENT TASK任务，也停止默认出厂EVENT TASK任务
  for task in user_event_tasks:
    task.stop()
  """
def write_file(filename, filecontentstr):
  try:
    f = open(filename, 'w')
    f.write(filecontentstr)
    f.close()
  except:
    pass

def begin_write_file(filename):
  try:
    f = open(filename, 'w+')
    f.write('\r\n')
    f.flush()
    f.close()
  except Exception as e:
    f.flush()
    f.close()
    print(e)
    pass

def append_write_file(filename, filecontentstr):
  try:
    f = open(filename, 'a+')
    f.write(filecontentstr)
    f.flush()
    f.close()
  except Exception as e:
    f.flush()
    f.close()
    print(e)
    pass
    
def reset_machine():
  machine.reset()






