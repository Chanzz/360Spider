import os
import xlrd
import xlwt

interest_point = []
people_tag = []
people_property = []
gouwu_interest_point = []
query_dstrb = []
active_app_dstrb = []
mapping = {"兴趣分布.xls": interest_point, "人群标签.xls": people_tag, "人口属性分布.xls": people_property,
           "购物兴趣分布.xls": gouwu_interest_point, "搜索词分布.xls": query_dstrb,
           "APP活跃分布.xls": active_app_dstrb}


def merge():
    path = '.\excel\\'
    folder_list = os.listdir(path)
    for i in folder_list:
        file = i.split('-')
        car_name = file[0]
        date = file[1]
        place = file[2]
        file_list = os.listdir(path + i)
        for file in file_list:
            excel = xlrd.open_workbook(path + i + '\\' + file)
            table = excel.sheet_by_index(0)
            len_rows = table.nrows
            len_cols = table.ncols
            for j in range(1, len_rows):
                values = []
                for k in range(len_cols):
                    value = str(table.cell_value(j, k))
                    values.append(value)
                values.extend([car_name, date, place])
                mapping[file].append(values)
    workbook = xlwt.Workbook(encoding='utf-8')
    for i in mapping:
        worksheet = workbook.add_sheet(i.split('.')[0])
        for j in range(len(mapping[i])):
            for k in range(len(mapping[i][j])):
                worksheet.write(j, k, mapping[i][j][k])
    workbook.save('全部.xls')


if __name__ == '__main__':
    merge()
