from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas 
import cv2
import urllib
import urllib.request
import numpy as np
import skimage
from skimage import measure, img_as_float
from skimage.io import imread
from skimage.metrics import structural_similarity as ssim
from skimage.transform import resize
from PIL import Image
import skimage.io as io
from skimage.io import imsave


rawList = pandas.read_excel("W:\Evan\python scripts\captions.spreadsheet\captionsdatasheet.xlsx", names=["Code", "Caption", "Id"])
#print (idLs[idLs.Id == idLs[0].Id])

opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36")
driver = webdriver.Chrome(options=opts)
driver.get("https://www.airbnb.com/login/")
elem = driver.find_element_by_id("signin_email").send_keys("airbnb@cabovillas.com")
elem = driver.find_element_by_id("signin_password").send_keys("Cant post this on github")
elem = driver.find_element_by_id("user-login-btn").click()


#https://www.tutorialkart.com/opencv/python/opencv-python-resize-image/
#img = cv2.imread(link, cv2.IMREAD_UNCHANGED)

def formatCaption(fileName):
    dashIndex = fileName.find("-")
    suffixIndex = fileName.find(".png")
    return fileName[dashIndex+1:suffixIndex]
def getLinks(id):
    driver.get("https://www.airbnb.com/manage-your-space/"+str(id)+"/details/photos")
    wait = WebDriverWait(driver, 5)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'photo-list__container')))
    imageElems = driver.find_elements_by_css_selector("img[src*='jpg'][data-index]")
    outLs = list([(int(elm.get_attribute("data-index")),elm.get_attribute("src")) for elm in imageElems])
    return outLs

def url_to_image(url):
    resp = urllib.request.urlopen(url)
    arr = np.asarray(bytearray(resp.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img_as_float(img)
    resized = resize(img, (76, 59))
    return resized


idLs = rawList.iloc[:, 2]
usefulLs = list(dict.fromkeys(idLs))

for curId in [usefulLs[0]]:
    thisRawList = rawList[rawList.Id==curId]
    pcLs = thisRawList.iloc[:, 1]
    thisCode = thisRawList.iloc[0,0]
    thisPath = "W:\Evan\python scripts\captions.spreadsheet\VRBO_captions\\" + thisCode + "\\"
    theseElems = getLinks(curId)
    for tup in theseElems:
        dataIndex = tup[0]
        url = tup[1]
        currentElem = driver.find_elements_by_css_selector("img[src*='jpg'][data-index]")[dataIndex-1]
        image1 = url_to_image(url)
        
        match = False
        for caption in pcLs: #the reason its navigating to the wrong picture/putting in the wrong caption has to do with j NOTE: J does not match index with caption
            image2 = cv2.imread(thisPath + caption)
            cv2.imwrite("converted.jpg", image2)
            image2 = cv2.imread("converted.jpg")
            image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
            image2 = resize(image2, (76, 59))
            ssim = measure.compare_ssim(image1, image2, data_range=6)
            if ssim > 0.66:
                currentElem.click()
                wait = WebDriverWait(driver, 10)
                descBox = wait.until(EC.element_to_be_clickable((By.NAME, 'photo_details_caption_input')))
                descBox.click()
                descBox.clear()
                descBox.send_keys(formatCaption(caption))
                
                saveButton = driver.find_elements_by_tag_name("button")[4]

                saveButton.click()
                driver.get("https://www.airbnb.com/manage-your-space/"+str(curId)+"/details/photos")
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'photo-list__container')))

                print("match found")
                print ("Local Path:")
                print(thisPath + caption)
                print ("ABB URL:")
                print (url)
