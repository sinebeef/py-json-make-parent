#!/usr/bin/python3

# Issues:

# Shower Door Seals : P14WS has variations, not by finish, but by glass width, 
# so 1/4" 3/4" etc so regular variation creation does not work..
# Solution: IMPORT AS SIMPLE PRODUCTS.
# Update: Does not work with mixed files where some have finishes used for _par
# and others are via the size

import json, re, time, sys
from copy import deepcopy

parts = sys.argv[1]

fin = {
    "GKCLR": "CLEAR",
    "CH": "CHROME",
    "HPSN": "SATIN NICKEL",
    "SN": "SATIN NICKEL",
        }

def load_jason(p):
    with open( p, "r") as r:
         meh = json.load(r) 
    return meh
    
def randFile( catname ):
    # Create a filename using category name for use in save file
    #a = 'crl_json_hinges_' + str(time.time()).split('.')[0] + '.json'
    a = 'crl_json_' + catname + '.json'
    return a

def uniq_records_for_fucks_sake(z):
    
    loaded_dicts = load_jason(z)
    
    # Set all products as stock 69 for testing. 
    # All stock will be updated before live
    #
    for record in loaded_dicts:
        # Set all products in stock. During dev
        record['Stock'] = "69"
        # If not price found, set to visually recognisable price
        if record['Pricing']['Price'] == "":
            record['Pricing']['Price'] = "12.34"
            
        if record['product_name'] == "":
            record['product_name'] = record['product_variation']
            
    series_of_dicts = {}

    for item in loaded_dicts:
        blah = {}
        id = item['product_number']
        blah[id] = item
        series_of_dicts.update(blah)
        blah = ""
    
    sorted_list = []

    for key,content in series_of_dicts.items():
        sorted_list.append(content)
    
    return sorted_list

def js_get_uniq_list_of_names(b):
    # Return uniq list of product_name from dict of products, these names are used to 
    # group together variations of the same product although with new parent sku method 
    # this may be redundant however it is the only primary method of grouping for parent 
    # child creation.
    #
    uniq_name_set = set()
    
    for names in b:
        if names['product_name']:
            uniq_name_set.add( names['product_name'] )
            
    return uniq_name_set

def checkForFinishes( rowz ):
    
    for row in rowz:
        # if finish is not empty
        if row['Finish']:
            # return with 1
            return 1
            
    # rows have no finishes so make
    # the more descriptive variation name
    # the product name
    
    for row in rowz:
        row['product_name'] = row['product_variation']
    return 0
 
 
#   Check the parent category, then check for product name in title
#   to be able to generate the "parent-cat>sub-cat>sub-cat" as per
#   http://www.wpallimport.com/documentation/taxonomies/nested/
#
def sortCategoryTree( rtm ):

    cat_dic =   {   'Hinges'        :{  'Geneva':'Geneva Hinges',
                                        'Victoria':'Victoria Hinges',
                                        'Prima':'Prima Hinges',
                                        'Milano':'Milano Hinges',
                                        'Monaco':'Monaco Hinges',
                                        'Madrid':'Madrid Hinges',
                                        'Grande':'Grande Hinges',
                                        'Estate':'Estate Hinges',
                                        'Melbourne':'Melbourne Hinges',
                                        'Concord':'Concord Hinges',
                                        'Classique':'Classique Hinges',
                                        'Cathedral':'Cathedral Hinges',
                                        'Pinnacle':'Pinnacle Hinges',
                                        'Cardiff':'Cardiff Hinges',
                                        'Cologne':'Cologne Hinges'}
    }
   
    for row in rtm:
    
        match = next((v for k, v in cat_dic[row['category']].items() if k in row['product_name']), None)
        if match: 
            row['category'] = row['category'] + ">" + match
            row['menu_order'] = '18'
                
    return

def js_add_parent(dic, names):
    # Return LIST variation with additional parent from cloned child with _par added to
    # sku to make unique
    
    # append to a all the rows that match this product name
    #
    rows_that_match = []
    
    for item in dic:
        if item['product_name'] == names:
            rows_that_match.append(item)

    # Create Cloned Parent Product
    # If product name appears more than once then it will be a variable
    # product item and needs a parent product. This parent will be created from
    # cloning the first item in the group and then nullifying the attributes so
    # as to not conflict with the origional product. Not knowing this caused me
    # hours of pain
    #
    if len(rows_that_match) > 1:
    
        # # remove these products because of scrape errors
        # for item in rows_that_match:
            # if item['product_name'] == "'D' Pull Handles":
                # return False
                
        # Add category tree for imports..
        #
        sortCategoryTree( rows_that_match )
        
        
        
        # rows_that_match is larger than one, but do any products have
        # have a ['finish'], if not they need to be as simple products
        # check for finishes using the function and then bail if none found
        #
        anyfinishes = checkForFinishes( rows_that_match )
        if anyfinishes == 0:
            return rows_that_match
        
        for item in rows_that_match:
            if item['Finish'] == "":
                foo = re.search(".*[0-9]+([A-Z]{2,6}$)",item['product_number'].strip())
                if foo:
                    try:
                        item['Finish'] = fin[foo.group(1)]
                    except:
                        item['Finish'] = ""
                    #print(list['product_number'] + " | " + foo.group(1))
                    #print(item['product_number'] + " | " + item['Finish'])
  
        # Finishes make the variation so if the title and finish is the same as another, that variation
        # breaks, so make the finish an alternative (not the best solution but fuck knows for now)
        
        finish_attr = []
        
        for item in rows_that_match:
        
            if item['Finish'] == "":
                continue
            if item['Finish'] in finish_attr:
                item['Finish'] = item['Finish'] + " ALT"
                
            if item['Finish'] in finish_attr:
                item['Finish'] = item['Finish'] + " 2"  

            if item['Finish'] in finish_attr:
                item['Finish'] = item['Finish'] + " 3" 
                            
            finish_attr.append(item['Finish'])

        # Pick variation to clone as parent. prioritise chrome/metalic looking one
        # so as to make shop/archive aesthetically pleasing.
        #
        for clone_index, row in enumerate(rows_that_match):
            if row['Finish'] == 'POLISHED CHROME':
              clone = deepcopy(row)
              break
            if row['Finish'] == 'CHROME':
              clone = deepcopy(row)
              break
            if row['Finish'] == 'SATIN CHROME':
              clone = deepcopy(row)
              break
            if row['Finish'] == 'POLISHED NICKEL':
              clone = deepcopy(row)
              break
            if row['Finish'] == 'SATIN NICKEL':
              clone = deepcopy(row)
              break           
            if row['Finish'] == 'BRUSHED SATIN CHROME':
              clone = deepcopy(row)
              break           
              
        else:
              clone_index = 0
              clone = deepcopy(rows_that_match[clone_index])
                
        modified_parent_sku = clone['product_number'] + '_par'
        
        # Parent clone must have certain attributes removed in order to not conflict with
        # the actual product that is cloned from (not sure why atm)
        #
        clone['product_number'] = modified_parent_sku
        clone['Finish'] = ""
        clone['Pricing']['Price'] = ""
        clone['More Details']['Shipping Weight'] = ""
        clone['More Details']['Length'] = ""
        clone['More Details']['Width'] = ""
        clone['More Details']['Height'] = ""

        #Update all the variations with the new parent sku
        #
        more_rows_that_match = []
        for items in rows_that_match:
            items['crl_parent'] = modified_parent_sku
            more_rows_that_match.append(items)
            
        # Insert the parent as the first list item because woocommerce needs it to be
        # first with the children following, This caused me more hours of pain
        #
        more_rows_that_match.insert(0, more_rows_that_match.pop(clone_index))
        more_rows_that_match.insert(0, clone)
        
        return more_rows_that_match
        
        #Only a single will be a simple product with no parent
    
    else:
        # print(rows_that_match)
        # if rows_that_match[0]['Pricing']['Price'] == "":
            # rows_that_match[0]['Pricing']['Price'] = "33.33"
            # rows_that_match[0]['Stock'] = "0"
        return rows_that_match 

updated = []        

# Create uniq dictionary records using the product_number
#
list_of_uniq_dicts = uniq_records_for_fucks_sake(parts)

catfname = list_of_uniq_dicts[0]['category'].lower().replace(' ','-')
if catfname == "":
    catfname = "no-cat-found"

unique_name_set = js_get_uniq_list_of_names(list_of_uniq_dicts)

for single_name in unique_name_set:
    grouped_products = js_add_parent(list_of_uniq_dicts, single_name)
    if grouped_products:
        updated += grouped_products
  
# Save the data to a json file which is a list of dicts that wpallimport loves
#
with open( randFile( catfname ),"w") as w:
    json.dump(updated, w, indent=2)
w.close() 
