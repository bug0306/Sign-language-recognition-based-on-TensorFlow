import os
import numpy as np
import cv2

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from translate import Translator

def main():
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface.xml")

    def predict(image_data):
        predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
        max_score = 0.0
        res = ''
        for node_id in top_k:
            human_string = label_lines[node_id]
            score = predictions[0][node_id]
            if score > max_score:
                max_score = score
                res = human_string
        return res, max_score

    label_lines = [line.rstrip() for line
                   in tf.io.gfile.GFile("logs/trained_labels.txt")]
    with tf.io.gfile.GFile("logs/trained_graph.pb", 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')
    with tf.compat.v1.Session() as sess:
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
        c = 0
        cap = cv2.VideoCapture(0)
        res, score = '', 0.0
        i = 0
        mem = ''
        consecutive = 0
        sequence = ''
        while True:
            ret, img = cap.read()
            img = cv2.flip(img, 1)
            if ret:
                x1, y1, x2, y2 = 100, 100, 300, 300
                img_cropped = img[y1:y2, x1:x2]
                c += 1
                image_data = cv2.imencode('.jpg', img_cropped)[1].tostring()
                a = cv2.waitKey(33)
                if i == 4:
                    res_tmp, score = predict(image_data)
                    res = res_tmp
                    i = 0
                    if mem == res:
                        consecutive += 1
                    else:
                        consecutive = 0
                    if consecutive == 2 and res not in ['nothing']:
                        if res == 'space':
                            sequence += ' '
                        elif res == 'del':
                            sequence = sequence[:-1]
                        else:
                            sequence += res
                        consecutive = 0
                i += 1
                cv2.putText(img, '%s' % (res.upper()), (100, 400), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 4)
                # cv2.putText(img, '(score = %.5f)' % (float(score)), (100,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
                mem = res
                cv2.rectangle(img, (x1, y1), (x2, y2), (125, 125, 0), 2)
                cv2.imshow("Webcam", img)
                img_sequence = np.zeros((200, 1200, 3), np.uint8)
                cv2.putText(img_sequence, '%s' % (sequence.upper()), (30, 30), cv2.FONT_HERSHEY_PLAIN, 1,
                            (255, 255, 255), 2)
                cv2.imshow("Text", img_sequence)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    with open("text.txt", "w") as f:
                        # translator = Translator(from_lang="english", to_lang="chinese")
                        # f = translator.translate(f)
                        f.write(str(sequence))
                    break
            else:
                break
        cv2.destroyAllWindows()
        cv2.VideoCapture(0).release()


if __name__ == "__main__":
    main()
