import requests, urllib3, os
from tkinter import *
from tkinter.ttk import *
from time import sleep
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# The format of the url is: https://interfacelift.com/wallpaper/details/WALLPAPER_NUM/
# We need to append the wallpaper number to then end of the url with the '/' or the page will not be found
# Starts at number 3 and goes to 4201, but there are only 3924 wallpapers
# 4201-3 = 3998; 3998-3924 = 74 missing pictures in the loop
# 393 total pages
# There is a

urllib3.disable_warnings()
res_dict = {}
wallpaper_links = []
selected_resolutions = ["1280x720 - 720p HDTV", "1920x1080 - 1080p HDTV", "2560x1440"]
wallpaper_errors = []
MAX_RES_SELECTIONS = 3
progressbar_position = 0
TOTAL_PAGES = 394
pageUrl = "http://interfacelift.com/wallpaper/downloads/date/any/index"  # + pageNUmber + ".html"
urlSuffix = ".html"

# example wallpaper link https://interfacelift.com/wallpaper/7yz4ma1/03144_albionfalls_2560x1440.jpg
baseWallpaperUrl = "https://interfacelift.com/wallpaper/7yz4ma1/0"
res1080 = "_1920x1080.jpg"
res1440 = "_2560x1440.jpg"

os.makedirs(os.getcwd() + "/Wallpapers/1920x1080/", exist_ok=True)
os.makedirs(os.getcwd() + "/Wallpapers/2560x1440/", exist_ok=True)
path1080 = os.getcwd() + "/Wallpapers/1920x1080/"
path1440 = os.getcwd() + "/Wallpapers/2560x1440/"


def build_dictionary_from_file():
    with open("res_list.txt") as file:
        file.readline()
        for line in file:
            (key, val) = line.split(':')
            res_dict[str(key)] = val


def build_image_url_without_res(image_name, image_id):
    return baseWallpaperUrl + image_id + "_" + image_name


def download_wallpaper_to_file(wallpaper_url, picture_info, session):
    # wallpaper_url = build_image_url(pictureInfo[0], pictureInfo[2])
    image_data = session.get(wallpaper_url, stream=True)
    if image_data.status_code == 200:
        if not os.path.exists(path1080 + picture_info[0] + ".jpg"):
            with open(path1080 + picture_info[0] + ".jpg", 'wb') as f:
                f.write(image_data.content)
                print("Downloaded " + picture_info[0] + ".jpg")
                return True
        else:
            print("Image " + picture_info[0] + ".jpg already exists.")
            return True
    else:
        print("Given resolution is not available for the current wallpaper: " + picture_info[2])
        print("Status code: " + image_data.status_code)
    return False


def scrape_wallpaper_page(page_num, session):
    page_num_string = str(page_num)
    wallpaper_url = pageUrl + page_num_string + urlSuffix

    response = session.get(wallpaper_url, verify=False)
    if not response.status_code == 200:
        wallpaper_errors.append([wallpaper_url, response.status_code])
        print(wallpaper_url + " has as problem: " + response.status_code)
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

            wallpaper_links.append(build_image_url_without_res(picture_info[0], picture_info[1]))

        print(wallpaper_url + " has been completed.")


def scrape_all_pages_for_wallpaper_urls():
    for pageNum in range(1, 394):
        scrape_wallpaper_page(pageNum)
        # page_num_as_string = str(pageNum)
        # new_url = pageUrl + page_num_as_string + urlSuffix
        #
        # response = session.get(new_url, verify=False)
        # if not response.status_code == 200:
        #     wallpaper_errors.append(pageNum)
        # else:
        #     soup = BeautifulSoup(response.text, features="lxml")
        #     functions = soup.find_all('select')
        #     for x in functions:
        #         onchange_func_text = x.get('onchange')
        #         starting_index = onchange_func_text.find("(")
        #         picture_info = onchange_func_text[starting_index:].replace("'", "")
        #         picture_info = picture_info.strip("()")
        #         picture_info = picture_info.split(",")
        #         del picture_info[1]
        #
        #         wallpaper_links.append(build_image_url_without_res(picture_info[0], picture_info[1]))
        #     print("Page " + page_num_as_string + " complete.")


def save_wallpaper_link_to_file():
    with open("wallpaper_links_without_res.txt", 'w') as text_file:
        for index in wallpaper_links:
            text_file.write("".join(index) + "\n")


def gui():
    tk = Tk()
    tk.title('InterfaceLIFT Bulk Wallpaper Downloader')
    # width x length
    tk.geometry("400x300")
    tk.resizable(False, False)

    selected_resolutions_list_box = Listbox(tk, width=40, height=10)
    selected_resolutions_list_box.grid(column=2, row=1)
    # Populate the ListBox with the preset resolutions (maybe change to just current res in the future)
    for x in selected_resolutions:
        selected_resolutions_list_box.insert('anchor', x)

    res_dropdown = Combobox(tk, state="readonly", width=30)
    res_dropdown['values'] = list(res_dict.keys())
    res_dropdown.current(0)
    res_dropdown.grid(column=2, row=2)

    def add_res_to_list():
        if res_dropdown.get() in selected_resolutions or len(selected_resolutions) >= MAX_RES_SELECTIONS:
            print("Resolution is already selected.")
        else:
            selected_resolutions.append(res_dropdown.get())
            selected_resolutions_list_box.insert('anchor', res_dropdown.get())
            print(selected_resolutions)

    # Button to add resolutions to the list of wallpaper downloads
    add_button = Button(master=tk, text="Add", command=add_res_to_list)
    add_button.grid(column=1, row=3)

    def remove_res_from_list():
        try:
            selected_resolutions.remove(selected_resolutions_list_box.get(selected_resolutions_list_box.curselection()))
            selected_resolutions_list_box.delete(selected_resolutions_list_box.curselection())
        except TclError:
            print("Nothing selected")

    remove_button = Button(master=tk, text="Remove", command=remove_res_from_list)
    remove_button.grid(column=3, row=3)

    def clear_list():
        selected_resolutions.clear()
        selected_resolutions_list_box.delete(0, END)

    clear_button = Button(master=tk, text="Clear List", command=clear_list)
    clear_button.grid(column=3, row=4)

    def refresh_command():

        def close_window():
            refresh_command.running = False
            popup.destroy()
            print("Window closed from X button")

        popup = Toplevel(tk)
        popup.protocol('WM_DELETE_WINDOW', lambda: close_window())
        popup.grab_set()
        Label(popup, text="Files being downloaded").grid(row=0, column=0)
        Label(popup, text="THE POPUP WINDOW FOR REFRESH").grid(row=1, column=0)

        # def handle_focus(event):
        #     print("I have gained the focus")
        # popup.bind("<FocusIn>", handle_focus)

        progress = 0
        progress_var = DoubleVar()
        progress_bar = Progressbar(popup, variable=progress_var, maximum=100)
        progress_bar.grid(row=2, column=0)  # .pack(fill=tk.X, expand=1, side=tk.BOTTOM)
        popup.pack_slaves()

        progress_step = float(100.0 / TOTAL_PAGES)
        refresh_command.running = True
        for page_num in range(TOTAL_PAGES):
            if refresh_command.running:
                popup.update()
                scrape_wallpaper_page(page_num)
                progress += progress_step
                progress_var.set(progress)
        refresh_command.running = False
        # progress_bar.destroy()
        # popup.destroy()

    fetch_urls_button = Button(master=tk, text="Refresh", command=refresh_command)
    fetch_urls_button.grid(column=2, row=3, pady=(10))

    def start_command():
        progressbar_var = DoubleVar()
        progressbar = Progressbar(tk, variable=progressbar_var, maximum=100, length=200)
        progressbar.grid(column=2, row=6)
        print("Starting")

    start_button = Button(master=tk, text="Start", command=start_command, width=20 )
    start_button.grid(column=2, row=7)

    tk.mainloop()


# def read_data_from_file():
#     reader = open("res_list.txt", 'r')
#     reader.readline()
#     for line in reader:
#         res_data = line.split(':')
#         res_labels.append(res_data[0])
#         res_dimensions.append(res_data[1])


def main():
    # read_data_from_file()

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    build_dictionary_from_file()
    gui()
    if os.path.exists("wallpaper_links_without_res.txt"):
        return True


if __name__ == '__main__':
    main()

# dat = {
#     "resolution": "1920x1080"
# }
# response = session.request()
# response = session.get(baseUrl, verify=False, params=dat).text

# soup = BeautifulSoup(response, features="lxml")
# wallpapers = soup.find_all("id=wallpaper")
# print(wallpapers)

# for x in range(0, 4202):
#     wallpaperNum = str(x)
#     newUrl = (baseUrl + wallpaperNum + "/")
#     response = session.get(newUrl, verify=False)
#     if response.status_code != 200:
#         missingTotal += 1
#         missingIDs.append(x)
#     print(newUrl + ": " + str(response.status_code))

# print(missingTotal)

# baseUrl = "http://interfacelift.com/wallpaper/details/4201/"
# pageUrlTest = "http://interfacelift.com/wallpaper/downloads/date/any/index1.html"

# response = session.get(pageUrl + "1.html", verify=False)
#     soup = BeautifulSoup(response.text, features="lxml")
#     functions = soup.find_all('option')
#
#     for x in functions:
#         text = x.text
#         value = x.get('value')
#         print(text + ':' + value)
