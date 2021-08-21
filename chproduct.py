import os
import machine
import ujson

DEFAULT_PRODUCT_NAME = 'cyberEye'
DEFAULT_PRODUCT_VERSION = '2000.3000.4000.5020' 
DEFAULT_LANGUAGE = 'en'

def registe_event_task(event_task):
  global user_event_tasks
  global MAX_EVENT_TASK_COUNT
  if len(user_event_tasks) < MAX_EVENT_TASK_COUNT:
    user_event_tasks.append(event_task)
    event_task.start()

def get_system_info(lang=None):

  try:
    f = open('/flash/system_config', 'r+')
  except:
    return DEFAULT_PRODUCT_NAME, DEFAULT_PRODUCT_VERSION, DEFAULT_LANGUAGE
    
  content = f.read()
  config = ujson.loads(content)
  
  if config['language'] != lang and lang: 
    config['language']=lang
    f.close()
    f = open('/flash/system_config', 'w')
    f.write(ujson.dumps(config))
    
  f.close()
  
  return config['product_name'], config['product_version'], config['language']

def product_name():

  productname, _, _ = get_system_info()

  return productname

def product_version():

  _, productver, _ = get_system_info()
  
  return productver

def product_lang():

  _, _, productlang = get_system_info()
  
  return productlang

def write_file(filename, filecontentstr):
  try:
    f = open(filename, 'w')
    f.write(filecontentstr)
    f.close()
  except:
    pass

def begin_write_file(filename):
  try:
    os.remove(filename)
    f = open(filename, 'w')
    f.close()
  except Exception as e:
    f = open(filename, 'w')
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


