
import json, os, glob, requests
from datetime import datetime, timezone




location_id = "67149847"
label_file_path = "/home/vixen/rs/dev/marlin_hp/hp_data"
user_uid = "0001vixen"
user_name = "Rahul"


path = f'{label_file_path}/{location_id}'
print (path)
filenames = [os.path.basename(x) for x in glob.glob(f'{label_file_path}/{location_id}/*')]


for filename in filenames:
    # print (filename)
    split_arr = filename.split('.')
   
    time_str = split_arr[1]
    
    yr_str = f'20{time_str[0]}{time_str[1]}'
    
    
    month_str = f'{time_str[2]}{time_str[3]}'
    date_str = f'{time_str[4]}{time_str[5]}'
    
    time_str = f'{yr_str}{month_str}{date_str}_{time_str[6]}{time_str[7]}{time_str[8]}{time_str[9]}{time_str[10]}{time_str[11]} UTC'
    # print (time_str)
    dt_obj = datetime.strptime(time_str, '%Y%m%d_%H%M%S %Z').replace(tzinfo=timezone.utc)
    # print (dt_obj.timestamp()*1000)
    
    start_time_ms = dt_obj.timestamp()*1000
    # print (start_time_ms)
    # print (filename)
    
    if filename != "67149847.140822155029.txt":
        continue
    
    with open(f'{path}/{filename}') as file:
        print (f'{path}/{filename}')
        
        for line in file:
           
            line_arr = line.split()
            if len(line_arr) < 3:
                # print (line_arr)
                continue
        
            # print (line_arr[2])
            print (float(line_arr[0]), float(line_arr[1]), line_arr[2])
            t_start_time_ms = start_time_ms + float(line_arr[0]) * 1000
            end_time_ms = start_time_ms + float(line_arr[1]) * 1000
            
            t_start_time_dt = datetime.fromtimestamp(t_start_time_ms/1000.0)
            end_time_dt = datetime.fromtimestamp(end_time_ms/1000.0)
            
            # print (start_time_ms)
            # print (t_start_time_ms)
            # print (end_time_ms)
            # print(t_start_time_dt)
            # print(end_time_dt)
            # exit()
            label = line_arr[2]
            
            # send label
         
            # print (f't_start_time_ms,  end_time_ms')
            # exit()
            post_data = {
                'snapshot_id':'point',
                'label': label,
                'signature_id': 'na',
                'user_uid': user_uid,
                'user_name': user_name,
                'start_time_ms' : t_start_time_ms,
                'end_time_ms': end_time_ms,
                'listener_location': location_id,
                'acoustic_filepath': "",
                'data_filepath' : ""
            }  
            # print (post_data)
            url = "https://vixen.hopto.org/rs/api/v1/data/signature";
            
            requests.post(url, data = json.dumps(post_data)) 
