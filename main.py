from tkinter import *
from tkinter.ttk import *

import os
import requests
import screeninfo
import urllib3
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# The wallpaper ids start 3 and goes to 4201, but there are only 3924 wallpapers, meaning some were removed.
# 4201-3 = 3998; 3998-3924 = 74 missing pictures
# 393 total pages of wallpapers to browse
# Data gathered from using the program.
# 720p - 2782 wallpapers, 2,156,455,510 bytes (2GB) 6:38.42 (no threading)
# 1080p - 2764 wallpapers, 4,395,560,751 bytes (4.09GB) 9:43.33 (no threading)
# 1440p - 2289 wallpapers, 6,589,693,875 bytes (6.13GB) 11:10.92 (no threading)

# InterfaceLIFT.com doesnt have SSL certificate up to date
# Output is cluttered with warnings with every web request
urllib3.disable_warnings()

# Only 3 resolutions to prevent ip blocking and long runtimes, and lots of disk usage
# Each resolution selected is sending 3924 requests and downloading almost that many files.
MAX_RES_SELECTIONS = 3
TOTAL_PAGES = 394
TOTAL_WALLPAPERS = 3924

# example wallpaper link http://interfacelift.com/wallpaper/downloads/date/any/index/1.html
BASE_WALLPAPER_BROWSE_URL = "http://interfacelift.com/wallpaper/downloads/date/any/index"
HTML_SUFFIX = ".html"
FILE_NOT_FOUND_URL = "http://interfacelift.com/site/404.php"
RES_ERROR_MESSAGE = "Invalid parameter: res"

# example wallpaper link that will redirect to the wallpaper
# https://interfacelift.com/wallpaper/7yz4ma1/03144_albionfalls_2560x1440.jpg
BASE_WALLPAPER_IMAGE_URL = "https://interfacelift.com/wallpaper/7yz4ma1/0"


def gui(session, wallpaper_links_arr, resolution_dictionary, selected_resolutions_arr, error_arr):
    tk = Tk()
    tk.title('InterfaceLIFT Wallpaper Downloader')
    # width x length
    tk.geometry("400x300")
    tk.resizable(False, False)

    selected_resolutions_list_box = Listbox(tk, width=40, height=10)
    selected_resolutions_list_box.grid(column=2, row=1)
    # Populate the ListBox with the preset resolutions (maybe change to just current res in the future)
    for x in selected_resolutions_arr:
        selected_resolutions_list_box.insert('anchor', x)

    res_dropdown = Combobox(tk, state="readonly", width=30)
    res_dropdown['values'] = list(resolution_dictionary.keys())
    res_dropdown.current(0)
    res_dropdown.grid(column=2, row=2)

    add_button = Button(master=tk, text="Add", command=lambda: add_res_to_list())
    add_button.grid(column=1, row=3)

    # fetch_urls_button = Button(master=tk, text="Refresh", command=lambda: refresh_command())
    # fetch_urls_button.grid(column=2, row=3, pady=(10))

    remove_button = Button(master=tk, text="Remove", command=lambda: remove_res_from_list())
    remove_button.grid(column=3, row=3)

    clear_button = Button(master=tk, text="Clear List", command=lambda: clear_list())
    clear_button.grid(column=3, row=4)

    start_button = Button(master=tk, text="Start", command=lambda: start_command(), width=20)
    start_button.grid(column=2, row=7)

    def add_res_to_list():
        if res_dropdown.get() in selected_resolutions_arr or len(selected_resolutions_arr) >= MAX_RES_SELECTIONS:
            print("Resolution is already selected.")
        else:
            selected_resolutions_arr.append(res_dropdown.get())
            selected_resolutions_list_box.insert('anchor', res_dropdown.get())
            print(selected_resolutions_arr)

    def remove_res_from_list():
        try:
            selected_resolutions_arr.remove(selected_resolutions_list_box.get(selected_resolutions_list_box.curselection()))
            selected_resolutions_list_box.delete(selected_resolutions_list_box.curselection())
        except TclError:
            print("Nothing selected")

    def clear_list():
        selected_resolutions_arr.clear()
        selected_resolutions_list_box.delete(0, END)

    # def refresh_command():
    #
    #     def close_window():
    #         refresh_command.running = False
    #         popup.destroy()
    #         print("Window closed from X button")
    #
    #     popup = Toplevel(tk)
    #     popup.protocol('WM_DELETE_WINDOW', lambda: close_window())
    #     popup.grab_set()
    #     Label(popup, text="Files being downloaded").grid(row=0, column=0)
    #     Label(popup, text="THE POPUP WINDOW FOR REFRESH").grid(row=1, column=0)
    #
    #     progress = 0
    #     progress_var = DoubleVar()
    #     progress_bar = Progressbar(popup, variable=progress_var, maximum=100)
    #     progress_bar.grid(row=2, column=0)  # .pack(fill=tk.X, expand=1, side=tk.BOTTOM)
    #     popup.pack_slaves()
    #
    #     progress_step = float(100.0 / TOTAL_PAGES)
    #     refresh_command.running = True
    #     for page_num in range(TOTAL_PAGES):
    #         if refresh_command.running:
    #             popup.update()
    #             scrape_page_for_wallpaper_urls(page_num, session)
    #             progress += progress_step
    #             progress_var.set(progress)
    #     refresh_command.running = False
    #     # progress_bar.destroy()
    #     # popup.destroy()

    def start_command():
        if len(selected_resolutions_arr) >= 1:
            start_button.destroy()
            add_button['state'] = DISABLED
            clear_button['state'] = DISABLED
            remove_button['state'] = DISABLED
            res_dropdown['state'] = DISABLED
            selected_resolutions_list_box['state'] = DISABLED
            start_command.downloading = True

            def stop_command():
                start_command.downloading = False
                stop_button.destroy()
                progressbar.destroy()
                new_start_button = Button(master=tk, text="Start", command=lambda: start_command(), width=20)
                new_start_button.grid(column=2, row=7)
                add_button['state'] = NORMAL
                clear_button['state'] = NORMAL
                remove_button['state'] = NORMAL
                res_dropdown['state'] = NORMAL
                selected_resolutions_list_box['state'] = NORMAL

            stop_button = Button(master=tk, text="Cancel", command=lambda: stop_command(), width=20)
            stop_button.grid(column=2, row=7)

            progressbar_var = DoubleVar()
            progressbar = Progressbar(tk, variable=progressbar_var, maximum=100, length=200)
            progressbar.grid(column=2, row=6)

            progress = 0
            progress_step = float(100.0 / TOTAL_WALLPAPERS * len(selected_resolutions_arr))
            for link in wallpaper_links_arr:
                if not start_command.downloading:
                    break
                for res in selected_resolutions_arr:
                    if not start_command.downloading:
                        break
                    tk.update()
                    resolution = str(resolution_dictionary.get(res))
                    download_wallpaper_to_file(session, link, resolution, error_arr)
                    progress += progress_step
                    progressbar_var.set(progress)
            stop_command()
        else:
            popup = Toplevel(height=500, width=600)
            popup.resizable(False, False)
            popup.grab_set()
            Label(popup, text="Please select at least one resolution.").pack()
            Button(master=popup, text="OK", command=lambda: popup.destroy(), width=20).pack()

    tk.mainloop()


def build_dictionary_from_file():
    resolution_dictionary = {}
    with open("res_list.txt") as file:
        # Skip the first line as it is just labels
        file.readline()
        for line in file:
            (key, val) = line.strip().split(':')
            resolution_dictionary[key] = val
    return resolution_dictionary


def get_user_screen_res(res_dict):
    user_resolutions = []
    for monitor in screeninfo.get_monitors():
        res_string = "{0}x{1}".format(monitor.width, monitor.height)
        for key in list(res_dict.keys()):
            if res_dict[key] == res_string:
                if res_string not in user_resolutions:
                    user_resolutions.append(res_string)
    return user_resolutions


def download_wallpaper_to_file(session, wallpaper_url, res, error_arr):
    file_path = "{0}/Wallpapers/{1}/".format(os.getcwd(), res)
    image_file_info = wallpaper_url[44:]
    file_name = "{0}{1}_{2}.jpg".format(file_path, image_file_info, res)
    appended_url = '{0}_{1}.jpg'.format(wallpaper_url, res)

    image_request = session.get(appended_url, verify=False)

    correct_status_code = image_request.status_code == 200
    correct_content_type = image_request.headers.get('Content-Type') == "image/jpeg"
    if correct_status_code and correct_content_type:
        if not os.path.exists(file_path):
            print("{0} wallpaper folder does not exist... creating {0} folder.".format(res))
            os.makedirs(file_path)

        with open(file_name, 'wb') as file:
            try:
                file.write(image_request.content)
                print("{0} has been downloaded.".format(file_name))
            except Exception as e:
                error_message = "Error downloading file. " + e.errno
                print(error_message)
    else:
        print("'{0}' resolution is not supported for the wallpaper {1}.".format(res, image_file_info))
        error_arr.append([appended_url, image_request.status_code])


def main():
    res_dict = build_dictionary_from_file()
    selected_resolutions = get_user_screen_res(res_dict)

    links_file = open("wallpaper_links_without_res.txt")
    wallpaper_links = links_file.read().splitlines()

    wallpaper_errors = []

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    gui(session, wallpaper_links, res_dict, selected_resolutions, wallpaper_errors)
    print(wallpaper_errors)


if __name__ == '__main__':
    main()


# DEVELOPER MODE FUNCTIONS TO BE ADDED LATER
def build_image_url_without_res(image_name, image_id):
    return "{0}{1}_{2}".format(BASE_WALLPAPER_IMAGE_URL, image_id, image_name)


def scrape_page_for_wallpaper_urls(page_num, session, error_arr):
    newly_scraped_wallpaper_links = []
    wallpaper_url = BASE_WALLPAPER_BROWSE_URL + str(page_num) + HTML_SUFFIX

    response = session.get(wallpaper_url, verify=False)
    if response.status_code != 200:
        error_arr.append([wallpaper_url, response.status_code])
        print("{0} has a problem: {1}".format(wallpaper_url, response.status_code))
    else:
        soup = BeautifulSoup(response.text, features="lxml")
        functions = soup.find_all('select')
        for x in functions:
            onchange_func_text = x.get('onchange')
            starting_index = onchange_func_text.find("(")
            picture_info = onchange_func_text[starting_index:].replace("'", "")
            picture_info = picture_info.strip("()")
            picture_info = picture_info.split(",")
            del picture_info[1]

            newly_scraped_wallpaper_links.append(build_image_url_without_res(picture_info[0], picture_info[1]))

        print("{0} has been completed.".format(wallpaper_url))
    return newly_scraped_wallpaper_links


def scrape_all_pages_for_wallpaper_urls():
    for page_num in range(1, TOTAL_PAGES):
        scrape_page_for_wallpaper_urls(page_num)


def save_wallpaper_links_to_file(wallpaper_links_arr):
    with open("wallpaper_links_without_res.txt", 'w') as text_file:
        for index in wallpaper_links_arr:
            text_file.write("".join(index) + "\n")
# END OF DEVELOPER FUNCTIONS
