#!/usr/bin/python3

import archive
import os


def format_ml_record(path, dates, actual_date, date_out):
    def get_num(date):
        if date is None:
            print("NO DATE FOUND FOR: {0}".format(path))
        res = int(float(date.strftime("%s"))/24/60/60)
        return res

    def get_freq(date):
        return len(dates[date])

    actual_num = get_num(actual_date)

    def adjust(value):
        return value - actual_num

    date_values = sorted(dates.keys())
    if len(date_values) == 0:
        res = "NONE"
        if date_out:
            return [
                path,
                None, 0, None, 0, None, 0,
                res
            ]
        else:
            no_date = -1000000
            return [
                path,
                no_date, 0, no_date, 0, no_date, 0,
                res
            ]

    min_date = date_values[0]
    max_date = date_values[-1]

    if len(date_values) > 2:
        mid_date = date_values[-2]
    else:
        mid_date = date_values[-1]

    m_dates = [min_date, mid_date, max_date]
    min_freq, mid_freq, max_freq = map(get_freq, m_dates)
    min_adj, mid_adj, max_adj = map(adjust, map(get_num, m_dates))

    res = ""
    if actual_date == max_date:
        res = "MAX"
    elif actual_date == mid_date:
        res = "MID"
    elif actual_date == min_date:
        res = "MIN"
    else:
        res = "NONE"

    if date_out:
        return [
            path,
            min_date, min_freq, mid_date, mid_freq, max_date, max_freq,
            res
        ]
    else:
        return [
            path,
            min_adj, min_freq, mid_adj, mid_freq, max_adj, max_freq,
            res
        ]


def create_ml_record_for(path, date_out):
    """Creates a ML record for the given contents."""

    dates = archive.get_dates_from_contents(path)
    date_actual = archive.get_date_from_string(path)

    return format_ml_record(path, dates, date_actual, date_out)


def create_dataset_for(path, date_out=False):
    path = os.path.expanduser(path)
    data = []
    for root, dirs, files, in os.walk(path):
        for name in files:
            if name == "result.txt":
                fullpath = os.path.join(root, name)
                res = create_ml_record_for(fullpath, date_out)
                data.append(res)
    return data


def generate_model_for(path, test_items, model_file):
    from sklearn import tree
    from sklearn.externals.six import StringIO
    import pydotplus as pydot

    dataset = create_dataset_for(path, False)
    print("Created dataset with {0} records.".format(len(dataset)))

    counter = 0
    steps = int(len(dataset)/test_items)

    training_features = []
    training_labels = []
    validation_features = []
    validation_labels = []

    for item in dataset:
        feature = item[1:-1]
        label = item[-1]

        # is validation item
        if (counter % steps) == 0:
            validation_features.append(feature)
            validation_labels.append(label)
        else:
            training_features.append(feature)
            training_labels.append(label)
        counter += 1

    print("Training with {0} records.".format(len(training_features)))
    clf = tree.DecisionTreeClassifier()
    clf.fit(training_features, training_labels)

    print("Validating with {0} records.".format(len(validation_features)))
    results = clf.predict(validation_features)
    failed = False
    for i in range(0, len(validation_features)):
        label = validation_labels[i]

        res = results[i]
        if res != label:
            failed = True
            print("Validation failed! Expected: %r. Actual: %r" % (label, res))

    # extra sanity checking
    print("Sanity-checking with {0} records.".format(len(training_features)))
    results = clf.predict(training_features)
    for i in range(0, len(training_features)):
        label = training_labels[i]

        res = results[i]
        if res != label:
            failed = True
            print("Sanity-checking failed! Expected: %r. Actual: %r" % (label, res))

    if failed:
        print("Validation failed. Not exporting model!")
        return

    print("Exporting model to file '{0}'.".format(model_file))

    dot_data = StringIO()
    tree.export_graphviz(clf, out_file=dot_data,
                         feature_names=[
                             "min_date", "min_freq",
                             "mid_date", "mid_freq",
                             "max_date", "max_freq",
                             "file_date", "file_abs_date",
                             "actual_date"
                         ],
                         class_names=[
                             "MAX", "MID", "MIN", "NONE"
                         ],
                         filled=True, rounded=True,
                         impurity=False)
    graph = pydot.graph_from_dot_data(dot_data.getvalue())
    graph.write_pdf(model_file)


def main():
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument("path", help="Path to document-archive used for training.")
    p.add_argument("--model", "-m", default="model.pdf", help="Output file with tree-model.")
    p.add_argument("--tests", "-t", default=100, type=int, help="Number of items used to validate model.")

    args = p.parse_args()
    generate_model_for(args.path, args.tests, args.model)


if __name__ == "__main__":
    main()
