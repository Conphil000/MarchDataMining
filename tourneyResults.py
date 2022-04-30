# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 16:31:47 2022

@author: Conor
"""

import pandas as pd
import numpy as np
import DataHandling
import os

first_year = 2000
last_year = 2023

drop_year = []

include = [i for i in np.arange(first_year,last_year) if i not in drop_year]

# 68 teams playing in single-elimination tournament

# 4 Regionals, west, south, east, midwest - > final 4 - > winner
# Don't need to predict who makes it into tourney

# Each year refer to teams as seeds.

def getEmbededTable(url):
    return \
        pd.read_html(
            url
        )[0]
def getStandings(conference,season):
    return \
        getEmbededTable(
            f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=cbb&url=%2Fcbb%2Fconferences%2F{conference}%2F{season}.html&div=div_standings"
        )
def getSeasonSummary(season):
    return \
       getEmbededTable(
           f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=cbb&url=%2Fcbb%2Fseasons%2F{season}.html&div=div_conference-summary"
       )
       
def getABV(x):
    drop_words = ['conference','league']
    x = x.lower()
    for drop in drop_words:
        x = x.replace(drop,'')
    x = x.strip().replace('  ',' ')
    if len(x.split(' ')) == 1:
        abv = x
    elif x.split(' ')[0] in ['big','pac']:
        abv = x.replace(' ','-')
    else:
        abv = ''.join([i[0] for i in x.split(' ')]+['c'])
    replace = \
        {'southeastern':'sec',
         'a1c':'atlantic-10',
         'usa':'cusa',
         'sbc':'sun-belt',
         'caac':'colonial',
         'aec':'america-east',
         'asc':'atlantic-sun',
         'gwc':'great-west',
         'mid-american':'mac',
         'mac':'meac',
         'mcc':'midwestern-collegiate',
         'pacific-10':'pac-10',
         'sac':'swac',
         'taac':'trans-america'
    }
    return \
        abv if abv not in replace else replace[abv]
        

def ABVReference(interval):
    allCodes = pd.DataFrame()
    for i in include:
        this_year = getSeasonSummary(i)[['Conference']]
        this_year['Year'] = i
        allCodes = pd.concat([allCodes,this_year])
    allCodes = allCodes.groupby(by='Conference')['Year'].max().reset_index(drop=False)
    allCodes['ABV'] = allCodes.apply(lambda x: getABV(x['Conference']),axis = 1)

    vc = allCodes['ABV'].value_counts()
    if len(vc[vc>1]) > 0:
        print('Some new division; you need to modify getABV to handle this new abreviation.')
        print(vc[vc>1])
        return pd.DataFrame({'Conference':[],'Year':[],'ABV':[]})
    else:
        return allCodes

dict1 = ABVReference(include)
dict1.apply(lambda x: getStandings(x['ABV'],x['Year']),axis = 1)

season = 2020
conference='cusa'

def madeNCAA_Tourney_Conference(conference,season):
    standings = \
        getStandings(conference, season)
        
    standings.columns = ['_'.join([i[0],i[1]] if 'Unnamed' not in i[0] else [i[1]]).strip() for i in standings.columns.values]
    # print(standings.shape)
    notes = standings.iloc[:,12]
    notes.fillna('',inplace = True)
    ncaa_rows = notes[notes.str.contains('NCAA Tournament')].index
    return standings.iloc[ncaa_rows,1].values.tolist()
dict1.apply(lambda x: madeNCAA_Tourney_Conference(x['ABV'], x['Year']),axis = 1)
abv = dict1

def NCAA_Tourney_Teams(season):
    if os.path.exists('.\\pklSupport\\knownTourney.pkl'):
        known = DataHandling.importPKL('knownTourney','.\\pklSupport')
    else:
        known = {}
    if season in known:
        return known[season]
    else:
        abvDict = ABVReference([season])[['Conference','ABV']]
        abvDict.index = abvDict['Conference']
        del abvDict['Conference']
        abvDict = abvDict.to_dict()['ABV']
        
        conferences = getSeasonSummary(season)['Conference'].tolist()
        madeTourney = []
        for conf in conferences:
            madeTourney += madeNCAA_Tourney_Conference(abvDict[conf], season)
        known[season] = madeTourney
        DataHandling.exportPKL(known,'knownTourney','.\\pklSupport')
        return madeTourney

test = NCAA_Tourney_Teams(2018)

def getSchoolABV(x):
    abv = x.replace(' ','-').lower()
    abv = abv.replace('&','')
    abv = abv.replace('(','')
    abv = abv.replace(')','')
    abv = abv.replace('.','-')
    abv = abv.replace("'",'')
    abv = abv.replace('--','-')
    
    replace = \
        {'tcu':'texas-christian',
         'nc-state':'north-carolina-state',
         'louisiana':'louisiana-lafayette',
         'uc-santa-barbara':'california-santa-barbara',
         'unc-wilmington':'north-carolina-wilmington',
         'unc-greensboro':'north-carolina-greensboro',
         'unc-asheville':'north-carolina-asheville',
         'uab':'alabama-birmingham',
         'utep':'texas-el-paso',
         'utsa':'texas-san-antonio',
         'cal-state-long-beach':'long-beach-state',
         'ut-arlington':'texas-arlington',
         'little-rock':'arkansas-little-rock',
         'uc-irvine':'california-irvine',
         'uc-davis':'california-davis'
    }
    return \
        abv if abv not in replace else replace[abv]
def getSchoolHistory(school):
    return \
        getEmbededTable(
            f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=cbb&url=%2Fcbb%2Fschools%2F{school}%2F&div=div_{school}"
        )

for i in include:
    for j in NCAA_Tourney_Teams(i):
        print(getSchoolABV(j))
        getSchoolHistory(getSchoolABV(j))
        
def main():
    pass
if __name__ == '__main__':
    test = main()