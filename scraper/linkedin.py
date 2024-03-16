from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from scraper.Domain import Profile
from scraper.Domain import License, Experience, Education, Project
from scraper.models import UserProfileHtml
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import copy
import re


class Linkedin:
    @staticmethod
    def scroll(driver):
        start = time.time()

        initialScroll = 0
        finalScroll = 1000

        while True:
            driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
            finalScroll += 1000
            time.sleep(0.1)
            end = time.time()
            if round(end - start) > 20:
                break

    @staticmethod
    def login_with_cookie(driver, cookie):
        driver.get("https://www.linkedin.com/login")
        driver.add_cookie({
            "name": "li_at",
            "value": cookie
        })

    @staticmethod
    def get_general_info(html: str) -> Profile:
        soup = BeautifulSoup(html, 'lxml')
        name = soup.find(
            'h1', {'class': 'text-heading-xlarge inline t-24 v-align-middle break-words'}).get_text().strip()
        try:
            title = soup.find('div', {'class': 'text-body-medium break-words'}).get_text().strip()
        except:
            title = ''

        try:
            description = soup.find('div', {
                'class': 'pv-shared-text-with-see-more full-width t-14 t-normal t-black display-flex align-items-center'}).find('span').get_text().strip()
        except:
            description = ''

        try:
            location = soup.find(
                'span', {'class': 'text-body-small inline t-black--light break-words'}).get_text().strip()
        except:
            location = ''
        return copy.deepcopy(Profile(name=name, title=title, description=description, location=location))

    @staticmethod
    def get_contact_info(html: str, profile: Profile):
        soup = BeautifulSoup(html, 'lxml')
        email_r = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        try:
            profile.phone_number = soup.find(
                'li', {'class': 'pv-contact-info__ci-container t-14'}).find('span').get_text().strip()
        except:
            profile.phone_number = ''
        try:
            datas = soup.find_all(
                'div', {'class': 'pv-contact-info__ci-container t-14'})
            profile.email = ''
            for i in datas:
                current = i.find('a').get_text().strip()
                if (re.fullmatch(email_r, current)):
                    profile.email = current
                    break
        except:
            profile.email = ''
        try:
            profile.web_page = soup.find(
                'li', {'class': 'pv-contact-info__ci-container link t-14'}).find('a').get_text().strip()
        except:
            profile.web_page = ''

        return profile

    @staticmethod
    def get_certifications(html: str, profile: Profile) -> Profile:
        soup = BeautifulSoup(html, 'lxml')
        id = 0

        try:
            list_off_licenses = soup.find(
                'ul',
                {'class': 'pvs-list'}
            ).find_all('li', {'class', 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})
        except:
            profile.licences = []

        for i in list_off_licenses:
            try:
                name = i.find(
                    'div',
                    {'class': 'display-flex align-items-center mr1 hoverable-link-text t-bold'}
                ).find('span').get_text().strip()

                try:
                    emitted_by = i.find('span', {'class': 't-14 t-normal'}).find('span').get_text().strip()
                except:
                    emitted_by = ''

                try:
                    expedition = i.find('span', {'class': 't-14 t-normal t-black--light'}
                                        ).find('span').get_text().strip().split(':')[-1].strip()
                except:
                    expedition = ''

                c_license = License(
                    id=id,
                    name=name,
                    emitted_by=emitted_by,
                    expedition=expedition
                )
                profile.licences.append(c_license)
                id += 1
            except:
                continue

        return profile

    @staticmethod
    def get_experience(html: str, profile: Profile) -> Profile:
        soup = BeautifulSoup(html, 'lxml')
        id = 0

        try:
            list_off_experiences = soup.find(
                'ul',
                {'class': 'pvs-list'}
            ).find_all('li', {'class', 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})
        except:
            profile.experiences = []

        for i in list_off_experiences:
            try:
                name = i.find(
                    'div', {'class': 'display-flex align-items-center mr1 hoverable-link-text t-bold'}).find('span').get_text().strip()
            except:
                try:
                    name = i.find('div', {'class': 'display-flex align-items-center mr1 t-bold'}
                                  ).find('span').get_text().strip()
                except:
                    continue

            current_experience = Experience(name=name, id=id)

            try:
                # group of experiences
                group = i.find('ul', {'class': 'pvs-list'})
                elemets = group.find_all('li', {'class': 'pvs-list__paged-list-item pvs-list__item--one-column'})
                temp_id = 0
                for j in elemets:
                    element_name = j.find(
                        'div', {'class': 'display-flex align-items-center mr1 hoverable-link-text t-bold'}).find('span').get_text().strip()

                    try:
                        element_time = j.find('span', {'class': 't-14 t-normal t-black--light'}
                                              ).find('span').get_text().strip()
                    except:
                        element_time = ''

                    try:
                        element_description = j.find(
                            'div', {'class': 'display-flex align-items-center t-14 t-normal t-black'}).find('span').get_text().strip()
                    except:
                        element_description = ''

                    sub_exprecience = Experience(id=temp_id, name=element_name,
                                                 time=element_time, description=element_description)
                    sub_exprecience.group = None
                    current_experience.group.append(sub_exprecience)
                    temp_id += 1
            except:
                current_experience.group = None

            if not current_experience.group:
                try:
                    time = i.find('span', {'class': 't-14 t-normal t-black--light'}).find('span').get_text().strip()
                except:
                    time = ''

                current_experience.time = time

                try:
                    element_description = i.find(
                        'div', {'class': 'display-flex align-items-center t-14 t-normal t-black'}).find('span').get_text().strip()
                except:
                    element_description = ''

                current_experience.description = element_description

            profile.experiences.append(current_experience)

            id += 1

        return profile

    @staticmethod
    def get_education(html: str, profile: Profile) -> Profile:
        soup = BeautifulSoup(html, 'lxml')

        try:
            list_off_education = soup.find(
                'ul',
                {'class': 'pvs-list'}
            ).find_all('li', {'class', 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})
        except:
            profile.education = []

        id = 0
        for i in list_off_education:
            try:
                name = i.find(
                    'div',
                    {'class': 'display-flex align-items-center mr1 hoverable-link-text t-bold'}
                ).find('span').get_text().strip()
            except:
                continue

            try:
                entity = i.find(
                    'span',
                    {'class': 't-14 t-normal'}
                ).find('span').get_text().strip()
            except:
                entity = ''

            try:
                time = i.find(
                    'span',
                    {'class': 't-14 t-normal t-black--light'}
                ).find('span').get_text().strip()
            except:
                time = ''

            current_education = Education(name=name, entity=entity, id=id)
            current_education.set_time(time)

            profile.education.append(current_education)
            id += 1
        return profile

    @staticmethod
    def get_projects(html: str, profile: Profile) -> Profile:
        soup = BeautifulSoup(html, 'lxml')

        try:
            list_off_projects = soup.find(
                'ul',
                {'class': 'pvs-list'}
            ).find_all('li', {'class', 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})
        except:
            profile.projects = []

        id = 0
        for i in list_off_projects:
            name = i.find('div', {'class': 'display-flex align-items-center mr1 t-bold'}
                          ).find('span').get_text().strip()
            time = i.find('span', {'class': 't-14 t-normal'}).find('span').get_text().strip()

            try:
                description = i.find(
                    'div', {'class': 'display-flex align-items-center t-14 t-normal t-black'}).find('span').get_text().strip()
            except:
                description = ''

            profile.projects.append(Project(id, name, time, description))
            id += 1

        return profile

    @staticmethod
    def select_lenguage(driver, lenguage_to_pick: str = 'en_US'):
        select = Select(driver.find_element(By.ID, 'globalfooter-select_language'))
        select.select_by_value(lenguage_to_pick)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        return lenguage_to_pick

    @staticmethod
    def get_profile_data(cookie: str, user: User, only_check: bool = False, just_li: bool = False) -> bool:
        service = Service(executable_path=r'/usr/local/bin/chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        Linkedin.login_with_cookie(driver, cookie)

        print(f'[Extracting] info cookie: {cookie} with user {user.username}')

        driver.get(f'https://www.linkedin.com/feed/')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        if len(driver.page_source) == 39:
            return False, "Ah, it appears there's a slight hiccup with your Token!"

        username = BeautifulSoup(driver.page_source, 'lxml').find(
            'div', {'class', 'feed-identity-module__actor-meta break-words'}).find('a', href=True)['href'].replace('/in/', '')[0:-1]

        print(f'[Extracting] LinkedIn username: {username}')

        driver.get(f'https://www.linkedin.com/in/{username}/')

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        if just_li:
            return True

        if '404' in driver.current_url:
            return False, "By the four Founders! No user hath been unearthed with this username from the depths of our magical archives!"

        if only_check:
            return True

        Linkedin.scroll(driver)

        print(f'[Extracting] Selection lenguage {Linkedin.select_lenguage(driver)}')

        profile = Linkedin.get_general_info(driver.page_source)

        print(f'[Extracting::{username}] General info loaded')

        driver.get(f'https://www.linkedin.com/in/{username}/overlay/contact-info/')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        profile = Linkedin.get_contact_info(driver.page_source, profile)

        print(f'[Extracting::{username}] General contact info loaded')

        driver.get(f'https://www.linkedin.com/in/{username}/details/certifications/')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        Linkedin.scroll(driver)
        profile = Linkedin.get_certifications(driver.page_source, profile)

        print(f'[Extracting::{username}] General certifications info loaded')

        driver.get(f'https://www.linkedin.com/in/{username}/details/experience/')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        Linkedin.scroll(driver)
        profile = Linkedin.get_experience(driver.page_source, profile)

        print(f'[Extracting::{username}] General experience info loaded')

        driver.get(f'https://www.linkedin.com/in/{username}/details/education/')

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        Linkedin.scroll(driver)
        profile = Linkedin.get_education(driver.page_source, profile)

        print(f'[Extracting::{username}] General education info loaded')

        driver.get(f'https://www.linkedin.com/in/{username}/details/projects/')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        Linkedin.scroll(driver)
        profile = Linkedin.get_projects(driver.page_source, profile)

        print(f'[Extracting::{username}] General projects info loaded')

        driver.close()
        profile = profile.serrialize()
        try:
            user = UserProfileHtml.objects.get(
                user=user
            )
            user.data = profile
            user.save()
        except UserProfileHtml.DoesNotExist:
            user = UserProfileHtml(
                user=user,
                data=profile
            )
            user.save()

        return True