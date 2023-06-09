from flask import Flask, request, json, jsonify, make_response
from crud import Crud
from routes_helper import RoutesHelper
import os
import requests

app = Flask(__name__)

#/api/users/register
@app.route('/api/users/register', methods=['POST'])
def create_user():
    #content_type = request.headers.get('Content-Type')
    user_table = Crud('user_')
    users = user_table.get_all_elements()
    json = request.json
    user_in_bd = False
    if all(key in json.keys() for key in ['email', 'pw', 'name']):
        for user in users:
            if(user['email'] == json['email']):
                user_in_bd = True
        if(not user_in_bd):
            cols, values = RoutesHelper.insert_element('user_', json.items())
            user_holder = user_table.getElements_and_operator(cols, values)
            user_row = user_holder[0]
            user_id = user_row['id']
            return make_response({
                'message': 'User created successfully',
                'user_id': user_id
            }),201
        else:
            return make_response({"error": "An account with this email already exists."}), 409
    else:
        message = 'Missing required fields'
        return make_response({'error': message}), 400
    

@app.route('/api/users/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('pw')

    users_table = Crud('user_')
    users = users_table.getElements_and_operator(['email', 'pw'], [email, password])
    if(users):
        for user in users:
            if(user['email'] == email and user['pw'] == password):
                message = {"message": "Logged in successfully.", 'user_id': user['id']}
                return make_response(message), 200
    message = {'error': 'Invalid username or password'}
    return make_response(message), 401

@app.route('/api/google/login', methods=['POST'])
def login_google():
    req = request.json

    name = req.get('name')
    email = req.get('email')
    

    if not (name and email):
        return make_response({'error':'Está em falta name ou email no body do request.'})

    users_table = Crud('user_')
    users = users_table.getElements_and_operator(['name','email'], [name, email])

    if(users):
        for user in users:
            if(user['email'] == email):
                message = {"message": "Log in com sucesso.", 'user_id': user['id']}
                return make_response(message), 200
    
    user_table = Crud('user_')

    req.update({'platform':'google'})
    cols, values = RoutesHelper.insert_element('user_', req.items())
    user_holder = user_table.getElements_and_operator(cols, values)
    user_row = user_holder[0]
    user_id = user_row['id']
    return make_response({
                'message': 'Utilizador criado com sucesso.',
                'user_id': user_id
    }),201

@app.route('/api/users/info', methods=['POST'])
def get_user():
    user_id = request.json.get('id')
    if user_id:
        users_table = Crud('user_')
        user = users_table.get_element_by_pk(user_id, 'id')
        if user:
            return make_response(user)
        else:   
            return make_response({'error':'User not found.'}), 404
    else:
        return make_response({'error':'Missing id field.'}), 404

@app.route('/api/users/update', methods=['POST'])
def update_user():
    json = request.json
    user_id = json.get('id') 
    if user_id:
        handler = Crud('user_')
        for key in json.keys():
            if key not in handler.get_columns():
                return make_response({'error':'Invalid fields for update.'})
        element = handler.get_element_by_pk(user_id, 'id')
        if(element):
            RoutesHelper.update_element('user_', json.items(), user_id)
            return make_response({'message':'Updated.'})
        else:   
            return make_response({'error':'User not found.'}), 404
    else:
        return make_response({'error':'Missing id field.'}), 404


@app.route('/api/products/search', methods=['POST']) # recebe um json com um elemento (coluna:valor) query coluna like valor
def get_products_like():
    json = request.json
    keys = list(json.keys())
    if len(keys) == 1:
        handler = Crud('product')
        db_columns = handler.get_columns()
        search_col = keys[0]
        if(search_col not in db_columns):
            return make_response({'error':'Missing a valid column to search.'}), 404
        search_value = json.get(search_col)
        if search_col:
            handler = Crud('product')
            items = handler.getElementsLike(search_col, search_value)
            return make_response(items)
    else:
        return make_response({'error':'Only 1 parameter can be sent.'})

@app.route('/api/products/info', methods=['POST'])
def get_product():
    product_id = request.json.get('id')
    if product_id:
        handler = Crud('product')
        product = handler.get_element_by_pk(product_id, 'id')
        if product:
            return make_response(product)
        else:   
            return make_response({'error':'Product not found.'}), 404
    else:
        return make_response({'error':'Missing id field.'}), 404

@app.route('/api/products/filter', methods=['POST'])
def get_product_by_filter():
    json = request.json
    handler = Crud('product')
    cols = handler.get_columns()

    if all(key in cols for key in json.keys()):
        cols = []
        values = []
        for col, value in json.items():
            cols.append(col)
            values.append(value)
        
        items = handler.getElements_and_operator(cols, values)
        if items:
            return make_response(items)
        else:
            return make_response({'error':'Products not found'}), 404
    else:
        return make_response({'error':'Invalid fields sent.'}), 400

@app.route('/api/categories/list', methods=['GET'])
def get_categories():
    handler = Crud('categories')
    categories_list = handler.get_all_elements()
    return make_response(categories_list)

@app.route('/api/models/search', methods=['POST'])
def get_models_like():
    json = request.json
    keys = list(json.keys())
    if len(keys) == 1:
        handler = Crud('model')
        db_columns = handler.get_columns()
        search_col = keys[0]
        if(search_col not in db_columns):
            return make_response({'error':'Missing a valid column to search.'}), 404
        search_value = json.get(search_col)
        if search_col:
            handler = Crud('model')
            items = handler.getElementsLike(search_col, search_value)
            return make_response(items)
    else:
        return make_response({'error':'Only 1 parameter can be sent.'})

@app.route('/api/models/info', methods=['POST'])
def get_model():
    product_id = request.json.get('id')
    if product_id:
        handler = Crud('model')
        product = handler.get_element_by_pk(product_id, 'id')
        views_value = product['views']
        views_value += 1
        handler.update_element(product_id, ['views'], [views_value], 'id')
        product = handler.get_element_by_pk(product_id, 'id')
        if product:
            return make_response(product)
        else:   
            return make_response({'error':'Model not found.'}), 404
    else:
        return make_response({'error':'Missing id field.'}), 404

@app.route('/api/models/filter', methods=['POST'])
def get_model_by_filter():
    json = request.json
    handler = Crud('model')
    cols = handler.get_columns()
    
    if all(key in cols for key in json.keys()):
        cols = []
        values = []

        for col, value in json.items():
            cols.append(col)
            values.append(value)
        
        items = handler.getElements_and_operator(cols, values)
        if items:
            return make_response(items)
        else:
            return make_response({'error':'Models not found'}), 404
    else:
        return make_response({'error':'Invalid fields sent.'}), 400
    
@app.route('/api/models/filterlike', methods=['POST'])
def get_model_by_filter_w_like():
    json = request.json
    handler = Crud('model')
    cols = handler.get_columns()

    if 'name' in json.keys():

        if all(key in cols for key in json.keys()):
            cols = []
            values = []
        else:
            return make_response({'error':'Invalid fields sent.'}), 400

        for col, value in json.items():
            cols.append(col)
            values.append(value)


        handler = Crud('model')
        cnx = handler.connect()
        cursor = cnx.cursor(prepared=True, dictionary=True)

        sql_query = f'SELECT * FROM {handler.table_name} WHERE '

        set_sql = []

        for i in range(len(cols)):
            if cols[i] == 'name':
                sql_query += cols[i] + ' like %s '
                set_sql. append(f'%{values[i]}%')
            else:
                sql_query += cols[i] + ' = ? '
                set_sql.append(values[i])
                
                 
            if i < ((len(cols) - 1)):
                
                sql_query += "and "

        sql_query += ';'
        print(sql_query)
        
        cursor.execute(sql_query, set_sql)
        
        result = cursor.fetchall()
        cursor.close()
        cnx.close()

        if result:
            return make_response(result), 200
    
        return make_response({'error':'Models not found'}), 404
            
    
        

@app.route('/api/models/price', methods=['POST'])
def get_prices():
    id_model = request.json.get('id_model')
    if id_model:
        handler = Crud('association')
        result = handler.get_elements_by_string_field('id_model', id_model)
        if result:
            prices = RoutesHelper.get_prices(result)
            return make_response(prices)
        else:
            return make_response({'error':'Models not found'}), 404
    else:
        return make_response({'error':'Missing id field.'}), 404

@app.route('/api/supermarket/info', methods=['POST'])
def get_supermarket():
    supermarket_id = request.json.get('id')
    if supermarket_id:
        handler = Crud('supermarket')
        supermarket = handler.get_element_by_pk(supermarket_id, 'id')
        if supermarket:
            return make_response(supermarket)
        else:   
            return make_response({'error':'Supermarket not found.'}), 404
    else:
        return make_response({'error':'Missing id field.'}), 404

@app.route('/api/users/lists/create', methods=['POST'])
def create_prod_list():
    handler = Crud('user_lists')
    json = request.json
    cols = handler.get_columns()
    if(json.get('user_id')):
        if (all(key in cols for key in json.keys())):
                cols, values = RoutesHelper.insert_element('user_lists', json.items())
                inserted_list = handler.getElements_and_operator(cols, values)
                list_row = inserted_list[0]
                list_id = list_row['id']
                return make_response({
                    'message': 'List created successfully',
                    'list_id': list_id
                }),201
        else:
            message = 'Some fields may be misspelled'
            return make_response({'error': message}), 400
    else:
        return make_response({'error':'Please specifie a user_id value.'}), 400

@app.route('/api/users/lists/update', methods=['POST'])
def update_lists():
    json = request.json
    list_id = json.get('id') 
    if list_id:
        handler = Crud('user_lists')
        for key in json.keys():
            if key not in handler.get_columns():
                return make_response({'error':'Invalid fields for update.'})
        element = handler.get_element_by_pk(list_id, 'id')
        if(element):
            RoutesHelper.update_element('user_lists', json.items(), list_id)
            return make_response({'message':'Updated.'})
        else:   
            return make_response({'error':'List not found.'}), 404
    else:
        return make_response({'error':'Missing id field.'}), 404

@app.route('/api/users/lists/delete', methods=['POST'])
def delete_list():
    json = request.json
    list_id = json.get('id')
    if list_id:
        list_handler = Crud('user_lists')
        prod_handler = Crud('product_list')
        prod_handler.delete_element(list_id, 'user_lists_id')
        list_handler.delete_element(list_id, 'id')
        return make_response({'message':'Deleted.'})
    else:
        return make_response({'error':'Please provide a list_id.'}), 404

@app.route('/api/users/lists/filter', methods=['POST'])
def get_users_lists():
    json = request.json
    user_id = json.get('user_id')
    if user_id:
        handler = Crud('user_lists')
        result = handler.get_elements_by_string_field('user_id', user_id)
        if result:
            return make_response(result)
        else:
            return make_response({'error':'Not found.'}), 404
    else:
        return make_response({'error':'Please provide a user_id.'}), 404
    

@app.route('/api/user/lists/products/create', methods=['POST'])
def add_product_to_user_list():
    json = request.json
    user_id = json.get('user_lists_id')
    model_id = json.get('model_id')
    if user_id and model_id:
        cols = []
        values = []

        for col, value in json.items():
                cols.append(col)
                values.append(value)

        handler = Crud('product_list')
        in_db = handler.getElements_and_operator(cols, values)
        if not in_db:
            handler.insert(cols, values)
            return make_response({'message':'Inserted.'})
        else:
            return make_response({'error':'This item is already in the list.'}), 409
        
    else:
        return make_response({'error': 'Missing required fields.'}), 404
    
@app.route('/api/user/lists/products/info', methods=['POST'])
def get_products_in_a_list():
    json = request.json
    list_id = json.get('id')
    if list_id:
        handler = Crud('product_list')
        products_list = handler.get_elements_by_string_field('user_lists_id', list_id)
        models =[]
        for list_row in products_list:
            model_id = list_row['model_id']
            model_handler = Crud('model')
            model= model_handler.get_element_by_pk(model_id, 'id')
            models.append({key:model[key] for key in model})
        return make_response(models)
    else:
        return make_response({'error':'Missing id field'}), 404

@app.route('/api/user/lists/products/delete', methods=['POST'])
def delete_product_in_a_list():
    json = request.json
    list_id = json.get('user_lists_id')
    model_id = json.get('model_id')
    if list_id and model_id:
        handler = Crud('product_list')
        
        cols = []
        values = []
        
        for col, value in json.items():
            cols.append(col)
            values.append(value)
        
        result = handler.getElements_and_operator(cols, values)
        if len(result) == 1:
            handler.delete_element(result[0]['id'], 'id')
            return make_response({'message':'Deleted.'})
        else:
            return make_response({'error': 'That item does not exist.'}), 404
    else:
        return make_response({'error': 'Missing required fields.'}), 404

@app.route('/api/cart/prices', methods=['POST'])
def get_cart_price():

    json = request.json
    models_qty = json.get('models_qty')
    
    if models_qty:
        json_holder = []
        # Aqui ta a puta armada
        
        for id_model, qty in models_qty:
            handler = Crud('association')
            result = handler.get_elements_by_string_field('id_model', id_model)
            
            if result:
                json_holder.append([RoutesHelper.get_prices(result), qty])
        
        continente_cart = 0
        auchan_cart = 0

        for models_list, qty in json_holder:
            for model in models_list:
                if model.get('supermarket_id') == 'Continente':
                    continente_cart += (round(model.get('price'), 2) * qty)
                if model.get('supermarket_id') == 'Auchan':
                    auchan_cart += (round(model.get('price'), 2) * qty)
        
        response_payload = []
        supermarkets = ['Continente', 'Auchan']
        carts = [continente_cart, auchan_cart]
        for x in range(2):
            response_payload.append({
                'supermarket': supermarkets[x],
                'cart': carts[x]
            })

        return make_response(response_payload), 200
    
    return make_response({'error':'Missing models_qty field.'}), 404



if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
