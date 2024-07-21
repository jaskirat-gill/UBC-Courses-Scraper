import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import multiprocessing

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
  startTime = time.time()
  print(f"Scraping courses for {subject_url}...")
  courses = []

  try:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument('--log-level=3')

    driver = webdriver.Chrome( options=options)
    driver.get(subject_url)



    # Wait for course rows to be present
    WebDriverWait(driver, 10).until(
      EC.presence_of_all_elements_located((By.TAG_NAME, 'tr')) 
    )

    course_rows = driver.find_elements(By.TAG_NAME, 'tr')
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

  except:
    pass

  endTime = time.time()
  elapsed_time = endTime - startTime
  print(f"Elapsed time for {subject_url}: {elapsed_time:.2f} seconds")
  return courses

def scrape_course_details(course_url):
  start_time = time.time()
  print(f"Scraping course details for {course_url}...")
  options = webdriver.ChromeOptions()
  options.add_argument("--headless") 
  options.add_argument('--log-level=3')

  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  driver.get(course_url)
  course_data = {}

  try:
    # Wait for description element to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.course-view__description p'))
    )


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
  except:
    pass  

  driver.quit()
  end_time = time.time()
  elapsed_time = end_time - start_time
  print(f"Elapsed time for {course_url}: {elapsed_time:.2f} seconds")
  return course_data

def scrape_courses_for_multiple_subjects(subject_links_chunk):
    courses = []
    for subject_url in subject_links_chunk:
        courses.extend(scrape_courses(subject_url))
    return courses

def scrape_course_details_helper(course):
    return scrape_course_details(course['url'])

def main():
    start_time = time.time()

    base_url = "https://courses.students.ubc.ca/browse-courses"

    # Scrape subjects
    subjects = scrape_subjects(base_url)
    
    total_subjects = len(subjects)
    print(f"Found {total_subjects} total subjects.")

    # Distribute course scraping across multiple processes
    with multiprocessing.Pool(processes=16) as pool:
        subject_links_chunks = [subjects[i:i+len(subjects)//16] for i in range(0, len(subjects), len(subjects)//16)]
        course_data_list = pool.map(scrape_courses_for_multiple_subjects, subject_links_chunks)

    # Flatten the list of courses
    all_courses = [course for sublist in course_data_list for course in sublist]
    total_courses = len(all_courses)

    print(f"Found {total_courses} total courses.")
    # Distribute course details scraping across multiple processes
    #with multiprocessing.Pool(processes=4) as pool:
     #   course_details_list = pool.map(scrape_course_details_helper, all_courses)

    # Combine course data and details
    #for course, details in zip(all_courses, course_details_list):
    #    course.update(details)
    #    scraped_courses += 1
    #    print(f"Scraped {scraped_courses}/{total_courses} courses")

    # Export to JSON
    with open('ubc_courses.json', 'w') as jsonfile:
        json.dump(all_courses, jsonfile, indent=4)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total scraping time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
  main()
