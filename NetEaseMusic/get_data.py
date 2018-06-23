
from selenium import webdriver
import csv

url = "http://music.163.com/#/discover/playlist/?order=hot&cat=%E5%85%A8%E9%83%A8&limit=35&offset=0"

driver = webdriver.PhantomJS()

csv_file = open("playlist.csv", "w", newline='')
writer = csv.writer(csv_file)
writer.writerow(['Title', 'PlayNum','Link'])

while url != 'javascript:void(0)':
	driver.get(url)
	driver.switch_to.frame("contentFrame")
	d = driver.find_element_by_id("m-pl-container").find_elements_by_tag_name("li")
	print(len(d))
	for i in range(len(d)):
		nb = d[i].find_element_by_class_name("nb").text
		if '万' in nb and int(nb.split("万")[0]) > 500:
			msk = d[i].find_element_by_css_selector("a.msk")
			writer.writerow([msk.get_attribute('title'), nb, msk.get_attribute('href')])


	url = driver.find_element_by_css_selector("a.zbtn.znxt").get_attribute('href')

csv_file.close()