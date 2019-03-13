# The Signal Path - DataPad ePaper Display
# Shahriar Shahramian / November 2018

import epd7in5b
import Image
import ImageDraw
import ImageFont
import calendar
import time
import requests
import sys
import json
import wand
from wand.display import display
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

EPD_WIDTH = 640
EPD_HEIGHT = 384
TODOIST_TOKEN = 'PUT YOUR ID HERE'
WEATHER_API = 'PUT YOUR ID HERE'

def main():
        global Debug_Mode; Debug_Mode = 0
        global do_screen_update; do_screen_update = 1
        global epd; epd = epd7in5b.EPD()
        if Debug_Mode == 0:
            epd.init()
        else:
            print('-= Debug Mode =-')
        global todo_response; todo_response = ''
        global cal_width; cal_width = 240
        global line_start; line_start = 48
        global weather_reponse
        global forecast_reponse

        # All fonts used in frames
        global font_cal; font_cal = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 16)
        global font_day; font_day = ImageFont.truetype('fonts/Roboto-Black.ttf', 110)
        global font_weather; font_weather = ImageFont.truetype('fonts/Roboto-Black.ttf', 20)
        global font_day_str; font_day_str = ImageFont.truetype('fonts/Roboto-Light.ttf', 35)
        global font_month_str; font_month_str = ImageFont.truetype('fonts/Roboto-Light.ttf', 25)
        global font_weather_icons; font_weather_icons = ImageFont.truetype('fonts/meteocons-webfont.ttf', 45)
        global font_tasks_list_title; font_tasks_list_title = ImageFont.truetype('fonts/Roboto-Light.ttf', 30)
        global font_tasks_list; font_tasks_list = ImageFont.truetype('fonts/tahoma.ttf', 12)
        global font_tasks_due_date; font_tasks_due_date = ImageFont.truetype('fonts/tahoma.ttf', 11)
        global font_tasks_priority; font_tasks_priority = ImageFont.truetype('fonts/tahoma.ttf', 9)
        global font_update_moment; font_update_moment = ImageFont.truetype('fonts/tahoma.ttf', 9)
        global icons_list; icons_list = {u'01d':u'B',u'01n':u'C',u'02d':u'H',u'02n':u'I',u'03d':u'N',u'03n':u'N',u'04d':u'Y',u'04n':u'Y',u'09d':u'R',u'09n':u'R',u'10d':u'R',u'10n':u'R',u'11d':u'P',u'11n':u'P',u'13d':u'W',u'13n':u'W',u'50d':u'M',u'50n':u'W'}

        calendar.setfirstweekday(0) # Monday is the first day of the week

        global todo_wait; todo_wait = 300
        global refresh_time; refresh_time = 900
        start_time = time.time() + refresh_time

        while True:
            query_todo_list()
            if (do_screen_update == 1):
                do_screen_update = 0
                refresh_Screen()
                start_time = time.time() + refresh_time
            elif (time.time() - start_time) > 0:
                print('-= General Refresh =-')
                refresh_Screen()
                start_time = time.time() + refresh_time
            time.sleep(todo_wait)

def query_todo_list():
    global todo_response
    global do_screen_update
    print('-= Ping ToDo API =-')
    while True:
        try:
            new_todo_response = requests.get("https://beta.todoist.com/API/v8/tasks", params={"token":TODOIST_TOKEN}).json()
            break
        except ValueError:
            print('-= ToDo API JSON Failed - Will Try Again =-')
            time.sleep(todo_wait)
        except:
            print('-= ToDo API Too Many Pings - Will Try Again =-')
            time.sleep(refresh_time)
    if ((new_todo_response) != (todo_response)):
        print('-= Task List Change Detected =-')
        do_screen_update = 1
        todo_response = new_todo_response
        return True

def query_weather():
    global weather_response
    global forecast_response
    print('-= Ping Weather API =-')
    while True:
        try:
            weather_response = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"appid":WEATHER_API, "zip":'07059,us'}).json()
            forecast_response = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={"appid":WEATHER_API, "zip":'07059,us'}).json()
            break
        except:
            print('-= Weather API JSON Failed - Will Try Again =-')
            time.sleep(refresh_time)

def refresh_Screen():
    global todo_response
    global Debug_Mode
    global weather_response

    # Create clean black frames with any existing Bitmaps
    image_black = Image.open('BK_Black.bmp')
    draw_black = ImageDraw.Draw(image_black)

    # Create clean red frames with any existing Bitmaps
    image_red = Image.open('BK_Red.bmp')
    draw_red = ImageDraw.Draw(image_red)

    # Calendar strings to be displayed
    day_str = time.strftime("%A")
    day_number = time.strftime("%d")
    month_str = time.strftime("%B") + ' ' + time.strftime("%Y")
    month_cal = str(calendar.month(int(time.strftime("%Y")), int(time.strftime("%m"))))
    month_cal = month_cal.split("\n",1)[1];
    update_moment = time.strftime("%I") + ':' + time.strftime("%M") + ' ' + time.strftime("%p")

    # This section is to center the calendar text in the middle
    w_day_str,h_day_str = font_day_str.getsize(day_str)
    x_day_str = (cal_width / 2) - (w_day_str / 2)

    # The settings for the Calenday today number in the middle
    w_day_num,h_day_num = font_day.getsize(day_number)
    x_day_num = (cal_width / 2) - (w_day_num / 2)

    # The settings for the month string in the middle
    w_month_str,h_month_str = font_month_str.getsize(month_str)
    x_month_str = (cal_width / 2) - (w_month_str / 2)

    draw_black.rectangle((0,0,240, 384), fill = 0) # Calender area rectangle
    draw_black.text((20, 190),month_cal , font = font_cal, fill = 255) # Month calender text
    draw_black.text((x_day_str,10),day_str, font = font_day_str, fill = 255) # Day string calender text
    draw_black.text((x_day_num,35),day_number, font = font_day, fill = 255) # Day number string text
    draw_black.text((x_month_str,150),month_str, font = font_month_str, fill = 255) # Month string text
    draw_black.line((10,320,230,320), fill = 255) # Weather line
    draw_black.line((250,320,640,320), fill = 0) # Footer for additional items
    draw_red.rectangle((245,0, 640, 55), fill = 0) # Task area banner
    draw_red.text((250,10), "Tasks", font = font_tasks_list_title, fill = 255) # Task text
    draw_black.text((585,370),update_moment,font = font_update_moment, fill = 255) # The update moment in Pooch

    # Check weather and poppulate the weather variables
    query_weather()
    current_weather = weather_response['weather'][0]['main']
    current_icon = weather_response['weather'][0]['icon']
    current_temp = str(int(weather_response['main']['temp']) - 273) + 'C'
    forecast_weather = forecast_response['list'][0]['weather'][0]['main']
    forecast_icon = forecast_response['list'][0]['weather'][0]['icon']
    forecast_temp_min_max = str(int(forecast_response['list'][0]['main']['temp_min']) - 273) + 'C \ ' + str(int(forecast_response['list'][0]['main']['temp_max']) - 273) + 'C'

    if (len(current_weather) >= 9):
        current_weather = current_weather[0:7] + '.'
    if (len(forecast_weather) >= 9):
        forecast_weather = forecast_weather[0:7] + '.'

    # The placement for weather icon
    w_weather_icon,h_weather_icon = font_weather_icons.getsize(icons_list[str(current_icon)])
    y_weather_icon = 320 + ((384 - 320) / 2) - (h_weather_icon / 2)

    # The placement for current weather string & temperature
    w_current_weather,h_current_weather = font_weather.getsize(current_weather)
    w_current_temp,h_current_temp = font_weather.getsize(current_temp)

    # The placement for forecast temperature string & temperatures
    w_forecast_temp_min_max,h_forecast_temp_min_max = font_weather.getsize(forecast_temp_min_max)
    w_forecast_weather,h_forecast_weather = font_weather.getsize(forecast_weather)

    draw_black.text((250,y_weather_icon),icons_list[str(current_icon)], font = font_weather_icons, fill = 0) # Diplay weather icon

    draw_black.text((250 + w_weather_icon + 10,327), current_weather, font = font_weather, fill = 0) # Display the current weather text
    draw_black.line((250 + w_weather_icon + 10,352,250 + w_weather_icon + 10 + w_current_weather,352), fill = 0) # Line below the current weather text
    x_current_temp = (w_current_weather - w_current_temp) / 2 + 250 + 10 + w_weather_icon # Location for the current temperature to be displayed
    draw_black.text((x_current_temp, 356), current_temp, font = font_weather, fill = 0) # The text of the current temperature

    x_arrow_symbol = 250 + w_weather_icon + 20 + w_current_weather # Location of the arrow to be displayed
    draw_black.rectangle((x_arrow_symbol, 350, x_arrow_symbol + 10,354), fill = 0) # Rectangle of the arrow
    draw_black.polygon([x_arrow_symbol + 10, 346, x_arrow_symbol + 16,352, x_arrow_symbol + 10,358], fill = 0) # Triangle of the arrow

    x_forecast_start = x_arrow_symbol + 16 + 10 # All forcasts to be displayed start at this position
    draw_black.text((x_forecast_start, 356), forecast_temp_min_max, font = font_weather, fill = 0) # The text of the forecast temperature
    draw_black.line((x_forecast_start, 352, x_forecast_start + w_forecast_temp_min_max, 352), fill = 0) # Line above the forecast weather temperature text
    x_forecast_weather = x_forecast_start + (w_forecast_temp_min_max - w_forecast_weather) / 2
    draw_black.text((x_forecast_weather, 327), forecast_weather, font = font_weather, fill = 0) # Display the forecast weather text

    draw_black.text((x_forecast_start + w_forecast_temp_min_max + 10,y_weather_icon),icons_list[str(forecast_icon)], font = font_weather_icons, fill = 0) # Diplay forecast weather icon

    line_location = 20
    for my_task in todo_response:
        item = str(my_task['content'])
        priority = str(my_task['priority'])

        if (len(item) > 55):
            item = item[0:55] + '...'

        current_date = int(datetime.date.today().strftime('%j')) + (int(time.strftime("%Y")) * 365)
        if 'due' in my_task:
            due_date = int(datetime.date(int(str(my_task['due']['date']).split('-')[0]), int(str(my_task['due']['date']).split('-')[1]), int(str(my_task['due']['date']).split('-')[2])).strftime('%j')) + (int(str(my_task['due']['date']).split('-')[0]) * 365)
        else:
            due_date = -1

        if (due_date < current_date and due_date > 0):
            temp_draw = draw_red
        else:
            temp_draw = draw_black

        temp_draw.text((265, line_start + line_location), item, font = font_tasks_list, fill = 0) # Print task strings
        temp_draw.chord((247.5, line_start + 2 + line_location, 257.5, line_start + 12 + line_location), 0, 360, fill = 0) # Draw circle for task priority
        temp_draw.text((250,line_start + 2 + line_location), priority, font = font_tasks_priority, fill = 255) # Print task priority string
        temp_draw.line((250,line_start + 18 + line_location, 640, line_start + 18 + line_location), fill = 0) # Draw the line below the task
        if 'due' in my_task:
            temp_draw.rectangle((595,line_start + 2 + line_location, 640, line_start + 18 + line_location), fill = 0) # Draw rectangle for the due date
            temp_draw.text((602.5, line_start + 3.5 + line_location),str(my_task['due']['string']), font = font_tasks_due_date, fill = 255) # Print the due date of task

        if (due_date < current_date and due_date > 0):
            draw_red = temp_draw
        else:
            draw_black = temp_draw
        line_location += 26
        if (line_start + line_location + 28 >= 320):
            draw_red.rectangle((550,line_start + 2 + line_location, 640, line_start + 18 + line_location), fill = 0) # Print larger rectangle for more tasks
            # The placement for extra tasks not shown
            notshown_tasks = '... & ' + str(len(todo_response) - 9) +  ' more ...'
            w_notshown_tasks,h_notshown_tasks = font_tasks_due_date.getsize(notshown_tasks)
            x_nowshown_tasks = 550 + ((640 - 550) / 2) - (w_notshown_tasks / 2)
            draw_red.text((x_nowshown_tasks, line_start + 3.5 + line_location), notshown_tasks,font = font_tasks_due_date, fill = 255) # Print identifier that there are tasks not shown
            break

    if Debug_Mode == 1:
        print('-= Viewing ePaper Frames... =-')
        image_black.save("Black_Frame.png")
        image_red.save("Red_Frame.png")
        wand.display.display(wand.image.Image(filename = "Black_Frame.png"))
        wand.display.display(wand.image.Image(filename = "Red_Frame.png"))
        print('-= ...Done =-')
    else:
        print('-= Updating ePaper... =-')
        epd.display_frame(epd.get_frame_buffer(image_black),epd.get_frame_buffer(image_red))
        print('-= ...Done =-')
if __name__ == '__main__':
    main()
