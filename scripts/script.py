import math
from shutil import copyfile
import random as rand
import tensorflow.compat.v1 as tf
import os
import glob
import pandas as pd
import io
import xml.etree.ElementTree as et
from collections import namedtuple
from PIL import Image
from object_detection.utils import dataset_util, label_map_util

LABELS = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/annotations/label_map.pbtxt'
ANNOTATIONS = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/annotations'
TRAIN = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/images/train'
TEST = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/images/test'
IMAGES = 'C:/projetos/vision-detect/media/'
SCRIPT = 'C:/projetos/vision-detect/TensorFlow/workspace/training_demo/scripts/preprocessing'

label_map = label_map_util.load_labelmap(LABELS)
label_map_dict = label_map_util.get_label_map_dict(label_map)


def prepare_data(objetos):
    arquivo = open(LABELS, 'w')
    arquivo.close()
    for objeto in objetos:
        update_labelmap(objeto)
        partition_dataset(objeto, 0.2)
    os.system('python {0}/generate_tfrecord.py -x {1} -l {2} -o {3}/train.record'.format(
        SCRIPT, TRAIN, LABELS, ANNOTATIONS))
    os.system('python {0}/generate_tfrecord.py -x {1} -l {2} -o {3}/test.record'.format(
        SCRIPT, TEST, LABELS, ANNOTATIONS))


# atualiza o arquivo de labels
def update_labelmap(objeto):
    arquivo = open(LABELS, 'a')
    arquivo.write("item{\n")
    arquivo.write("    id: {0}\n".format(str(objeto.id)))
    arquivo.write("    name: '{0}'\n".format(objeto.nome))
    arquivo.write("}\n")
    arquivo.close()


def partition_dataset(objeto, percent):
    # preparação das pastas
    train_dir = os.path.join(TRAIN)
    test_dir = os.path.join(TEST)
    source_dir = os.path.join(IMAGES + objeto.pasta)

    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    # lista as imagens da pasta
    images = [f for f in os.listdir(source_dir) if '.jpg' in f]

    # calcula a separação do total de imagens para treino e teste
    num_images = len(images)
    num_test_images = math.ceil(percent * num_images)

    # adiciona parte dos arquivos a pasta teste
    for i in range(num_test_images):
        id_image = rand.randint(0, len(images) - 1)
        filename = images[id_image]
        xml_filename = os.path.splitext(filename)[0] + '.xml'
        copyfile(os.path.join(source_dir, filename), os.path.join(test_dir, filename))
        copyfile(os.path.join(source_dir, xml_filename), os.path.join(test_dir, xml_filename))
        images.remove(images[id_image])

    # adiciona o restante dos arquivos a pasta train
    for filename in images:
        copyfile(os.path.join(source_dir, filename), os.path.join(train_dir, filename))
        xml_filename = os.path.splitext(filename)[0] + '.xml'
        copyfile(os.path.join(source_dir, xml_filename), os.path.join(train_dir, xml_filename))


def generate_records(path, record):
    # criando arquivo .record
    writer = tf.io.TFRecordWriter(record)
    path = os.path.join(path)
    # criando dataframe com os arquivos .xml
    examples = xml_to_csv(path)
    # criando estrutura com o label_map
    grouped = split(examples, 'filename')
    for group in grouped:
        # cria o record com base nas imagens e labels
        tf_example = create_tf_example(group, path)
        writer.write(tf_example.SerializeToString())
    writer.close()
    print('Successfully created the TFRecord file: {}'.format(record))


def xml_to_csv(path):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = et.parse(xml_file)
        root = tree.getroot()
        filename = root.find('filename').text
        width = int(root.find('size').find('width').text)
        height = int(root.find('size').find('height').text)
        for member in root.findall('object'):
            bndbox = member.find('bndbox')
            value = (filename,
                     width,
                     height,
                     member.find('name').text,
                     int(bndbox.find('xmin').text),
                     int(bndbox.find('ymin').text),
                     int(bndbox.find('xmax').text),
                     int(bndbox.find('ymax').text),
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height',
                   'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]


def class_text_to_int(row_label):
    return label_map_dict[row_label]


def create_tf_example(group, path):
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    image_format = b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(row['xmin'] / width)
        xmaxs.append(row['xmax'] / width)
        ymins.append(row['ymin'] / height)
        ymaxs.append(row['ymax'] / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(row['class']))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example

