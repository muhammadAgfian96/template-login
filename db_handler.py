import numpy as np
import skimage
import os
import skimage
import shutil
import socket
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import json
import skimage.io
import skimage.draw
from bson.objectid import ObjectId

def crop_img_square(img, x, y):
    """ Crop a single image"""
    xmin = np.min(x)
    xmax = np.max(x)
    xmid = (xmax + xmin) // 2
    xdist = xmax - xmin

    ymin = np.min(y)
    ymax = np.max(y)
    ymid = (ymin + ymax) // 2
    ydist = ymax - ymin

    dist = np.max([xdist, ydist])
    half_dist = np.ceil(dist / 2.0)

    xmin = xmid - half_dist
    xmax = xmid + half_dist
    ymin = ymid - half_dist
    ymax = ymid + half_dist

    if xmin < 0:
        xmax = xmax - xmin
        xmin = 0

    if xmax >= img.shape[1]:
        xmin = xmin - (img.shape[1] - 1 - xmax)
        xmax = img.shape[1] - 1

    if ymin < 0:
        ymax = ymax - ymin
        ymin = 0

    if ymax >= img.shape[1]:
        ymin = ymin - (img.shape[1] - 1 - ymax)
        ymax = img.shape[1] - 1
    ymin = int(ymin)
    ymax = int(ymax)
    xmin = int(xmin)
    xmax = int(xmax)
    crop_dim = [ymin, ymax, xmin, xmax]
    img_out = img[ymin:ymax, xmin:xmax, :]
    img_out = np.copy(img_out)
    x_out = x - xmin
    y_out = y - ymin

    return img_out.astype(dtype=img.dtype), x_out, y_out, crop_dim


def crop_single_region(img, region):
    x_anno = np.array(region['shape_attributes']['all_points_x'], dtype=np.int)
    y_anno = np.array(region['shape_attributes']['all_points_y'], dtype=np.int)

    img_out, x, y, crop_dim = crop_img_square(np.copy(img), x_anno, y_anno)

    img_crp = np.zeros([*img_out.shape[:2], 4], dtype=img.dtype)
    img_crp[:, :, :3] = img_out[:, :, :3]

    rr, cc = skimage.draw.polygon(y, x)
    pos = np.concatenate([rr.reshape([-1, 1]), cc.reshape([-1, 1])], axis=1)
    pos = pos[pos[:, 0] < img_crp.shape[0], :]
    pos = pos[pos[:, 0] >= 0, :]
    pos = pos[pos[:, 1] >= 0, :]
    pos = pos[pos[:, 1] < img_crp.shape[1], :]
    if np.issubdtype(img_crp.dtype, np.integer):
        img_crp[pos[:, 0], pos[:, 1], 3] = 255
    else:
        img_crp[pos[:, 0], pos[:, 1], 3] = 1

    return img_crp, x_anno, y_anno, x, y


class Database_Pusher:
    def __init__(self, **kwargs):
        # os.umask(775)
        # self.umask = os.umask(775)
        self.params = {
                'ori_image_dir': './ori_image/',
                'output_image_dir': '/mnt/hdd_1/data/databases/imgs/',
                'ori_anno_dir': './ori_anno/',
                'output_anno_dir': '/mnt/hdd_1/data/databases/annos/',
                'output_ffb_img_dir': '/mnt/hdd_1/data/databases/ffbs/',
                'collector': 'Annon',
                'annotator': 'Annon',
                'notes': list(),
                'HOST': '127.0.0.1',
                'PORT': int(27017),
                'USER': 'binshouser',
                'PASS': 'qmDooVu9SSOb5ksFagblUH6aAcy4Fbp1',
                'DB': 'dummy',
                # 'DB': 'ffbdataset',
                'tags': []
                }
        self.params.update(kwargs)

        if not os.path.isdir(self.params['output_image_dir']):
            os.makedirs(self.params['output_image_dir'])
        if not os.path.isdir(self.params['output_anno_dir']):
            os.makedirs(self.params['output_anno_dir'])
        if not os.path.isdir(self.params['output_ffb_img_dir']):
            os.makedirs(self.params['output_ffb_img_dir'])

        self.host = socket.gethostbyname(self.params['HOST'])
        self.mongo_connect = MongoClient(self.params['HOST'], self.params['PORT'], username=self.params['USER'], password=self.params['PASS'],
            authSource=self.params['DB'], authMechanism='SCRAM-SHA-256')
        self.mongo_db = self.mongo_connect[self.params['DB']]
        self.ffb_collection = self.mongo_db['FFBs']
        self.anno_collection = self.mongo_db['Annotations']
        self.img_collection = self.mongo_db['FullImages']

        pass

    def process_single_region(self, img, iregion, region, maturity, freshness, ratdamage, full_img_uid):

        # x = np.array(region['shape_attributes']['all_points_x'], dtype=np.int)
        # y = np.array(region['shape_attributes']['all_points_y'], dtype=np.int)
        ffb_uid = ObjectId()
        ffb_img_dir = os.path.join(self.params['output_ffb_img_dir'], str(full_img_uid))

        if not os.path.isdir(ffb_img_dir):
            os.makedirs(ffb_img_dir)

        ffb_img_filename = str(ffb_uid) + '.png'

        region_item = {
            'uid': ffb_uid,
            'full_img_uid': full_img_uid,
            'img_dir': ffb_img_dir,
            'img_filename': ffb_img_filename,
            'maturity': maturity,
            'freshness': freshness,
            'ratdamage': ratdamage,
            'other_grades': list(),
            'date_added': datetime.datetime.now(),
            'tags': self.params['tags']
        }

        ffb_img, x_anno, y_anno, x, y = crop_single_region(img, region)
        skimage.io.imsave(os.path.join(os.path.join(ffb_img_dir, region_item['img_filename'])), ffb_img)

        self.ffb_collection.insert(region_item)

        pass

    def process_single_file(self, anno, key, anno_uid):

        img_uid = ObjectId()
        _, ext = os.path.splitext(anno['filename'])
        filename = str(img_uid) + ext

        img_item = {
            'uid': img_uid,
            'anno_key': key,
            'anno_uid': anno_uid,
            'img_dir': self.params['output_image_dir'],
            'img_filename': filename,
            'img_ori_filename': anno['filename'],
            'collector': self.params['collector'],
            'annotator': self.params['annotator'],
            'notes': self.params['notes'],
            'info': list(),
            'date_added': datetime.datetime.now(),
            'tags': self.params['tags']
        }

        img_full_path = os.path.join(self.params['ori_image_dir'], anno['filename'])

        if os.path.isfile(img_full_path):
            img = skimage.io.imread(img_full_path)
            skimage.io.imsave(os.path.join(self.params['output_image_dir'], filename), img)
            self.img_collection.insert(img_item)

            for iregion, region in enumerate(anno['regions']):
                maturity = self.MaturityList[region['region_attributes']['maturity']]
                freshness = self.FreshnessList[region['region_attributes']['freshness']]
                ratdamage = self.RatDamaged[region['region_attributes']['ratdamage']]
                self.process_single_region(img, iregion, region, maturity, freshness, ratdamage, img_uid)

        pass

    def process_anno_file(self, annos, anno_ori_filename):
        if '_via_img_metadata' in annos:

            self.MaturityList = annos['_via_attributes']['region']['maturity']['options']
            self.FreshnessList = annos['_via_attributes']['region']['freshness']['options']
            self.RatDamaged = annos['_via_attributes']['region']['ratdamage']['options']
            annos = annos['_via_img_metadata']


        for key in annos:
            anno = annos[key]
            anno_uid = ObjectId()

            anno_item = {
                'uid': ObjectId(),
                'anno_dir': self.params['output_anno_dir'],
                'anno_ori_filename': anno_ori_filename,
                'date_added': datetime.datetime.now(),
                'tags': self.params['tags']
            }

            src_path = os.path.join(self.params['ori_anno_dir'], anno_ori_filename)
            dst_path = os.path.join(self.params['output_anno_dir'], str(anno_uid) + '.json')

            shutil.copyfile(src_path, dst_path)
            self.anno_collection.insert(anno_item)
            self.process_single_file(anno, key, anno_uid)

        pass

    def process_full_directory(self, **kwargs):
        self.params.update(kwargs)

        for filename in os.listdir(self.params['ori_anno_dir']):
            name, ext = os.path.splitext(filename)
            if ext == '.json':
                filepath = os.path.join(self.params['ori_anno_dir'], filename)
                if os.path.isfile(filepath):
                    f = open(filepath, 'r')
                    annos = f.read()
                    f.close()
                    annos = json.loads(annos)
                    self.process_anno_file(annos, filename)

        pass

    def process_single_annotation_file(self, filepath, anno_ori_filename):
        if os.path.isfile(filepath):
            f = open(filepath, 'r')
            annos = f.read()
            f.close()
            annos = json.loads(annos)
            self.process_anno_file(annos, anno_ori_filename)
        pass

# maturity = ['Ungraded', 'Unripe', 'Underripe', 'Ripe', 'Overripe', 'Empty', 'NA']
# freshness = ['Ungraded', 'Fresh', 'Overnight', 'Old', 'NA']
# ratdamage = ['False', True, 'Ungraded', 'NA']


class Database_Puller:
    def __init__(self, **kwargs):
        # os.umask(775)
        # self.umask = os.umask(775)
        self.params = {
                'img_dir': '/mnt/hdd_1/data/databases/imgs/',
                'anno_dir': '/mnt/hdd_1/data/databases/annos/',
                'ffb_img_dir': '/mnt/hdd_1/data/databases/ffbs/',
                'notes': list(),
                'HOST': '10.8.0.10',
                'PORT': int(27017),
                'USER': 'binshouser',
                'PASS': 'qmDooVu9SSOb5ksFagblUH6aAcy4Fbp1',
                'DB': 'dummy',
                # 'DB': 'ffbdataset',
                'grade_type': 'maturity',
                'selected_grades': ['Ungraded', 'Unripe', 'Underripe', 'Ripe', 'Overripe', 'Empty'],
                'tags': None
                }

        self.params.update(kwargs)

        self.grade_map = dict()
        igrade = 0
        for key in self.params['selected_grades']:
            self.grade_map[key] = igrade
            igrade += 1

        self.host = socket.gethostbyname(self.params['HOST'])
        self.mongo_connect = MongoClient(self.params['HOST'], self.params['PORT'], username=self.params['USER'], password=self.params['PASS'],
            authSource=self.params['DB'], authMechanism='SCRAM-SHA-256')
        self.mongo_db = self.mongo_connect[self.params['DB']]
        self.ffb_coll = self.mongo_db['FFBs']
        self.anno_collection = self.mongo_db['Annotations']
        self.img_collection = self.mongo_db['FullImages']


    def update_rat_damage_value(self, id_:str, value:str, tags:str='ratdamage_updated'):
        res = {
            'found':False,
            'updated_ratdamage':False,
            'updated_tags':False,
        }
        res_ratdmg = self.ffb_coll.update_one(
            {'_id': ObjectId(id_)}, 
            {'$set': {'ratdamage': value}},
        )


        one_data_result = self.ffb_coll.find({'_id':id_})
        one_data = [doc for doc in one_data_result][0]

        
        if 'ratdamage_updated' not in one_data['tags']:
            res_tags = self.ffb_coll.update_one(
                {'_id': ObjectId(id_)}, 
                {'$push': {'tags': tags}},
            )
            if res_tags.modified_count > 0: res['updated_tags'] = True
        else:
            res['updated_tags'] = True



        if res_ratdmg.matched_count > 0: res['found'] = True
        if res_ratdmg.modified_count > 0: res['updated_ratdamage'] = True
        
        return res
    
    def get_data_by_id(self, id_):
        try:
            result = self.ffb_coll.find({'_id':ObjectId(id_)})
            data = dict()
            for doc in result:
                data.update(doc)
        except :
            data = False
        return data
    
    def get_one_data(self):
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
        # result = self.ffb_coll.find_one({"tags": {"$ne": 'ratdamage_updated'}})
        result = self.ffb_coll.aggregate([
                    { "$match": { "tags": { "$ne": ['ratdamage_updated'] } } },
                    # { "$match": { "tags": { "$in": ['ratdamage_updated'] } } },
                    { "$sample": { "size": 1 } }
                ])
        for doc in result:
            data = doc
        return dict(data)