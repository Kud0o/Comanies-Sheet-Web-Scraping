import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from tqdm import tqdm

def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

#content = requests.get('https://www.eyeofriyadh.com/ar/directory/category/1_business-money')
#content = requests.get('https://www.eyeofriyadh.com/ar/directory/index.php?category=4&name=government-sectors&page=4&ipp=400')
#content = content.text
#soup =  BeautifulSoup(content,features="lxml")
url_start = 'https://www.eyeofriyadh.com'
#table_of_contents = html_soup.find(id='toc')
#print(soup.find_all('div', class_='col-md-4 col-sm-4 col-xs-4'))
Areas_ = []
Names_ = []
Mobiles_ = []
Mails_ = []
Sites_ = []
Categories_ = []
References = []

#Catygories_links  = [ url_start+ x['href'] for x in soup.find_all('a', style="font-size:14px; color:#777;")]
Catygories_links = [f'https://www.eyeofriyadh.com/ar/directory/index.php?location=all&page={page}&ipp=80' for page in range(1,52)]
for Category_link in tqdm(Catygories_links):
    #print(Category_link)
    category_content = requests.get(Category_link).text
    category_soup = BeautifulSoup(category_content,features="lxml")

    Companies_links  = [ url_start+ x['href'] for x in category_soup.find_all('a', style="color:#000; font-weight:600; font-size:12px;")]
    
    for Company in tqdm(Companies_links):
        #print(Company)
        Company_content = requests.get(Company).text
        Company_soup = BeautifulSoup(Company_content,features="lxml")
        if Company_soup.text.__contains__('Page Not Found') :
            continue
        References.append(Company)
        Category_Type = [   type.text for type in 
                                [ line for line in
                                        Company_soup.find_all('div',style = re.compile('float:right; max-width: 565px;'))[0].find_all('a',href = re.compile('/ar/[a-z/0-9_]'),recursive=False) 
                                ]
                        ]
        Category_Type = [Category_Type[x:x+100] for x in range(0, len(Category_Type), 2)]
        Categories = ''
        for i in Category_Type:
            if len(i)>0:
                Categories = Categories+f'{i[0]} '
            if len(i) > 1:
                Categories = Categories+f'> {i[1]} ,'
        Categories= Categories[0:-2]
        Categories_.append(Categories)
        Area = Company_soup.find_all('ul','list')[0].text
        Name = Company_soup.find_all('h1',style=re.compile("font-size:22px;"))[0].text	
        Mobile = [Mob.text for Mob in Company_soup.find_all('a',href=re.compile('tel:[+0123456789 -]'))]
        Mail = [cfDecodeEmail(mail['href'].split('#')[1]) for mail in Company_soup.find_all('a',href=re.compile('/cdn-cgi/l/email-protection#[+0123456789 a-zA-Z]'))]
        Site = 	[site.text for site in Company_soup.find_all('a',text = re.compile('[a-z.](.com|.net|.org|.sa)'),recursive=True)]
        #print(f'{Area} , {Name} {Mobile} , {Mail} , {Site}')
        Areas_.append(Area)
        Names_.append(Name)
        Mobiles_.append(Mobile)
        Mails_.append(Mail)
        Sites_.append(Site)
        
DataFrame = pd.DataFrame({'Name':Names_, 'Mobile':Mobiles_,'Mail':Mails_,'Site':Sites_, 'Areas': Areas_,'Link':References,'Category':Categories_})
print(DataFrame)
#table_of_contents = soup.find(text='clear',recursive=True)
#print(table_of_contents)

file_name = 'SA_Companies_Sheet_all.xlsx'
  
# saving the excel
DataFrame.to_excel(file_name)