import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_subjects(base_url):
  print("Scraping subjects...")

  driver = webdriver.Chrome()
  driver.get(base_url)

  # Find all alphabet buttons
  alphabet_buttons = WebDriverWait(driver, 20).until(
      EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.subjects-table-filters__btn'))
  )
  subjects = []
  alphabet_buttons[0].click()

    # Wait for content to load
  WebDriverWait(driver, 10).until(
  EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.tss-1qtl85h-MUIDataTableBodyCell-root'))
  )

  while True:
    # Extract subject links
      subject_elements = driver.find_elements(By.TAG_NAME, 'tr')
      for element in subject_elements:
        try:
          subject_link_element = element.find_element(By.CSS_SELECTOR, 'td:first-child a')
          subject_link = subject_link_element.get_attribute('href')
          subjects.append(subject_link)
        except:
          pass  
        

      # Check for next page button
      next_page_button = driver.find_element(By.ID, 'pagination-next')
      if not next_page_button.is_enabled():
        break

      next_page_button.click()
      WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.tss-1qtl85h-MUIDataTableBodyCell-root'))
      )

  driver.quit()
  print("Finished scraping subjects.")
  return subjects

def scrape_courses(subject_url):
  print(f"Scraping courses for {subject_url}...")

  driver = webdriver.Chrome()
  driver.get(subject_url)

  # Wait for course rows to be present
  WebDriverWait(driver, 10).until(
      EC.presence_of_all_elements_located((By.TAG_NAME, 'tr')) 
  )

  course_rows = driver.find_elements(By.TAG_NAME, 'tr')
  courses = []
  for course_row in course_rows:
    try:
      course_data = {}

      # Extract course code and URL
      course_code_element = course_row.find_elements(By.TAG_NAME, 'a')[0]
      course_data['code'] = course_code_element.text
      course_data['url'] = course_code_element.get_attribute('href')

      # Extract course title
      course_title_element = course_row.find_elements(By.TAG_NAME, 'a')[1]
      course_data['title'] = course_title_element.text
      courses.append(course_data)
    except:
      pass

  driver.quit()
  print(f"Finished scraping courses for {subject_url}.")
  return courses

def scrape_course_details(course_url):
  print(f"Scraping course details for {course_url}...")

  driver = webdriver.Chrome()
  driver.get(course_url)

  # Wait for description element to be present
  WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, '.course-view__description p'))
  )

  course_data = {}

  # Extract course description
  description_element = driver.find_element(By.CSS_SELECTOR, '.course-view__description p')
  course_data['description'] = description_element.text.strip()

  # Extract course credits
  try:
    credits_element = driver.find_element(By.CSS_SELECTOR, '#course-view > div > div > div.course-view__tables > div > div > div:nth-child(2) > div > div:nth-child(3)')
    credits_text = credits_element.text.strip()
    credits = int(credits_text.split("\n")[1])  # Extract the numeric part
    course_data['credits'] = credits
  except:
    course_data['credits'] = ""

  driver.quit()
  print(f"Finished scraping course details for {course_url}.")
  return course_data


def main():
  base_url = "https://courses.students.ubc.ca/browse-courses"
  #subject_links = scrape_subjects(base_url)

  all_courses = []
  #for subject_link in tsubject_links:
  #courses = scrape_courses(subject_link)
  #print(courses)
  #for course in courses:
  course = {'code': 'AANB_V 500', 'url': 'https://courses.students.ubc.ca/browse-courses/course/COURSE_DEFINITION-3-18_20240901', 'title': 'Graduate Seminar'}
  course_details = scrape_course_details(course['url'])
  course.update(course_details)
  all_courses.append(course)

  with open('ubc_courses.json', 'w') as jsonfile:
      json.dump(all_courses, jsonfile, indent=4)

if __name__ == "__main__":
  main()
