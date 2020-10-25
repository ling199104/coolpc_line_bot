# import sqlite3


# connector = sqlite3.connect('db.sqlite3')
# table initialize
def table_init(connector):
    c = connector.cursor()
    # 資料建立時間、資料更新時間、商品屬類、商品名稱、商品圖片
    # 商品價格、商品是否特價、商品是否熱賣、被檢索次數、被估價次數
    c.execute(
        '''CREATE TABLE products (create_date timestamp, update_date timestamp, item_type text, item_name text,
        item_img blob, price integer, on_sale integer, hot_sale integer, search_count integer, match_count integer)'''
    )
    # 資料建立時間、資料更新時間、類別名稱
    # 類別內參數：商品熱賣數、圖片數、文章數、價格異動數、現實下殺數
    c.execute(
        '''CREATE TABLE types (create_date timestamp, update_date timestamp, type_name text,
        hot_sale integer, image_count integer, discussion integer, price_changed integer, on_sale integer)'''
    )

    # Save (commit) the changes
    connector.commit()
    connector.close()

# # Insert a row of data
# c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
