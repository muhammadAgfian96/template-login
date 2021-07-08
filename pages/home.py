import streamlit as st
import cv2
import os
from db_handler import Database_Puller as db
from bson.objectid import ObjectId
import numpy as np
from PIL import Image


db_handler = db()

def hr(place):
    place.markdown('<hr>', unsafe_allow_html=True)

def home_page(state):
    '''Anotating'''
    if state.curr_dir is None:
        state.curr_dir = 0
    if state.history is None:
        state.history = {}

    col1, col2, col3, col4 = st.beta_columns((1,1,2,2))


    # =============== Searching ==================
    state.input_id = col3.text_input('Id to search')
    status_search = st.empty()
    if col4.button('Search'):
        result = db_handler.get_data_by_id(state.input_id)
        if result == False:
            status_search.error('not Fond!')
        else:
            status_search.success('Found!')
            state.data = result
            state.img_file = os.path.join(state.data['img_dir'], state.data['img_filename'])
            # state.img_display = cv2.imread(state.img_file)
            state.img_display = condition_image(state.img_file)
    
    # find
    id_container = col2.empty()
    if col1.button('Get Image'):
        get_one_random_data(state)
        print('asd', str(state.data['_id']))

    col_img, col_history = st.beta_columns((5,2))
    hr(st.sidebar)
    st.sidebar.info('*Data Info*')
    data_container = st.sidebar.empty()
    
    if state.data is not None:
        label_this(state)
        id_container.write(f"id: {state.data['_id']}")
        my_data = {
            'Id': str(state.data['_id']), 
            'Date Added' : state.data['date_added'].strftime("%m/%d/%Y, %H:%M:%S"),
            'Rat_Damage' : state.data['ratdamage'],
            'Maturity' : state.data['maturity'],
            'freshness' : state.data['freshness'],
            'other_grades' : state.data['other_grades'],
            'tags' : state.data['tags'],
        }
        data_container.write(my_data)

    slide_history(state)

    # display img
    if state.img_display is not None:
        st.sidebar.write('**Dimention**')
        st.sidebar.write('height :', state.img_display.size[1])
        st.sidebar.write('width  :', state.img_display.size[0])
        # st.sidebar.write('channel:', state.img_display.shape[2])
        col_img.image(state.img_display, channels="BGR")
    else:
        col_img.warning('Cant Read the Image or No Data!')
    if col_history.button('Clear History'):
        state.history = {}

    col_history.write('**History:**')
    col_history.write(state.history)

def label_this(state):
    # max_len = len(ls_imgs)

    hr(st.sidebar)
    st.sidebar.write('**Labeling**')
    status = st.sidebar.empty()
    col = st.sidebar.beta_columns((1,1,1))


    # ================ Rat_Dmg ======================
    if col[0].button('🐀\nRat_Dmg'):
        # update
        updated_data = db_handler.update_rat_damage_value(
            id_=state.data['_id'],
            value='Yes')

        if updated_data['found'] == False:
            status.error('Not found files!')
        if updated_data['found'] and updated_data['updated_ratdamage'] and updated_data['updated_tags']:
            status.success('Updated: 🐀 rat_dmg')
            state.history[str(state.data['_id'])] = 'Yes'
            get_one_random_data(state)
        elif updated_data['updated_ratdamage'] == False and updated_data['found']:
            status.warning('No Update data!')
            state.history[str(state.data['_id'])] = 'Yes'
            get_one_random_data(state)
        else:
            status.error('Failed update!')


    # ================ NOT SURE ======================
    if col[1].button('😕  Not_sure'):
        # update
        updated_data = db_handler.update_rat_damage_value(
            id_=state.data['_id'],
            value='Ungraded')

        if updated_data['found'] == False:
            status.error('Not found files!')

        if updated_data['found'] and updated_data['updated_ratdamage'] and updated_data['updated_tags']:
            status.success('Updated: 😕 Not_sure')  
            state.history[str(state.data['_id'])] = 'Ungraded'
            get_one_random_data(state)
        elif updated_data['updated_ratdamage'] == False and updated_data['found']:
            state.history[str(state.data['_id'])] = 'Ungraded'
            status.warning('No Update data!')
            get_one_random_data(state)
        else:
            status.error('Failed update!')


    # ================ NORMAL ======================
    if col[2].button('🌴  Normal'):
        updated_data = db_handler.update_rat_damage_value(
            id_=state.data['_id'],
            value='No')

        if updated_data['found'] == False:
            status.error('Not found files!')
        if updated_data['found'] and updated_data['updated_ratdamage'] and updated_data['updated_tags']:
            status.success('Updated: 🌴 No')   
            state.history[str(state.data['_id'])] = 'No'
            get_one_random_data(state)
        elif updated_data['updated_ratdamage'] == False and updated_data['found']:
            state.history[str(state.data['_id'])] = 'No'
            status.warning('No Update data!')
            get_one_random_data(state)
        else:
            status.error('Failed update!')
        

def slide_history(state):
    # max_len = len(ls_imgs)
    hr(st.sidebar)

    list_file_id = sorted(list(state.history.keys()))
    max_len = len(list_file_id)
    if len(list_file_id) <= 0:
        return

    # st.sidebar.success('Annotations')
    st.sidebar.write('**History Annotated**')
    col = st.sidebar.beta_columns((1,1))


    if col[0].button('Previous'):
        if state.curr_dir <=0:
            pass
        else:
            state.curr_dir -= 1
            state.data = db_handler.get_data_by_id(list_file_id[state.curr_dir])
            state.img_file = os.path.join(state.data['img_dir'], state.data['img_filename'])
            # state.img_display = cv2.imread(state.img_file)
            state.img_display = condition_image(state.img_file)


    if col[1].button('Next'):
        if state.curr_dir == max_len-1:
            st.sidebar.info('Habis!')
            st.balloons()
            pass
        else:
            state.curr_dir += 1
            state.data = db_handler.get_data_by_id(list_file_id[state.curr_dir])
            state.img_file = os.path.join(state.data['img_dir'], state.data['img_filename'])
            # state.img_display = cv2.imread(state.img_file)
            state.img_display = condition_image(state.img_file)
    
    hr(st.sidebar)
    st.sidebar.info('*Path Image*')
    if state.img_file:
        st.sidebar.code(f"{state.img_file}", language="bash")
    


def get_one_random_data(state):
    """
        {'_id': ObjectId('606d776631276201e6b44f30'),
        'uid': ObjectId('606d776631276201e6b44f2f'),
        'full_img_uid': ObjectId('606d776631276201e6b44f2d'),
        'img_dir': '/mnt/hdd_1/data/databases/ffbs/606d776631276201e6b44f2d',
        'img_filename': '606d776631276201e6b44f2f.png',
        'maturity': 'Unripe',
        'freshness': 'Ungraded',
        'ratdamage': 'Ungraded',
        'other_grades': [],
        'date_added': datetime.datetime(2021, 4, 7, 17, 12, 6, 253000),
        'tags': ['reject_20210125', 'unorganized', 'partial_anno', 'mill']}
    """
    state.data = db_handler.get_one_data()
    state.img_file = os.path.join(state.data['img_dir'], state.data['img_filename'])
    # state.img_display = cv2.imread(state.img_file)
    state.img_display = condition_image(state.img_file)


@st.cache()
def load_images():
    path = 'db_images'
    images = os.listdir(path)
    curr_dir = os.getcwd()
    ls_imgs = [os.path.join(curr_dir, path, img) for img in images]
    return ls_imgs


def condition_image(img_path):
    image = Image.open(img_path)
    return image