from flask_restx import Namespace, Resource, fields
from ..models.orders import Order
from ..models.users import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus

orders_namespace = Namespace('orders', description='Orders related operations')

order_model = orders_namespace.model(
    'Order', {
        'id': fields.Integer(description="An Id"),
        'size': fields.String(description='Size of order', required=True,
                              enum=['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE']),
        'order_status': fields.String(description="The status of the Order", required=True,
                                      enum=['PENDING', 'IN_TRANSIT', 'DELIVERED']),
    }
)

order_status_model = orders_namespace.model(
    "OrderStatus",{
        'order_status': fields.String(required=True, description="Order Status",
                                      enum=['PENDING', 'IN_TRANSIT', 'DELIVERED'])

    }
)


@orders_namespace.route('')
class OrderGetCreate(Resource):

    @orders_namespace.marshal_with(order_model)
    @orders_namespace.doc(
        description="Retrieve all orders"
    )
    @jwt_required()
    def get(self):
        """
            Get all orders
        """
        orders = Order.query.all()

        return orders, HTTPStatus.OK

    @orders_namespace.expect(order_model)
    @orders_namespace.marshal_with(order_model)
    @orders_namespace.doc(
        description="Place an order"
    )
    @jwt_required()
    def post(self):
        """
            Create new orders
        """
        data = orders_namespace.payload
        username = get_jwt_identity()
        current_user = User.query.filter_by(username=username).first()
        new_order = Order(
            size=data['size'],
            flavour=data['flavour'],
            quantity=data['quantity']
        )
        if current_user is not None:
            new_order.user = current_user.id
        new_order.save()
        return new_order, HTTPStatus.CREATED


@orders_namespace.route('/order/<int:order_id>')
class GetUpdateDelete(Resource):
    @orders_namespace.marshal_with(order_model)
    @orders_namespace.doc(
        description="Retrieve an order by ID"
    )
    @jwt_required()
    def get(self, order_id):
        """
            Retrieve an order
        """
        order = Order.get_by_id(order_id)
        return order, HTTPStatus.OK

    @orders_namespace.expect(order_model)
    @orders_namespace.marshal_with(order_model)
    @orders_namespace.doc(
        description="Update an order"
    )
    def put(self, order_id):
        """
            Update an order by id
        """
        order = Order.get_by_id(order_id)
        data = orders_namespace.payload
        order.size = data['size']
        order.flavour = data['flavour']
        order.quantity = data['quantity']

        order.commit()
        return order, HTTPStatus.OK

    @orders_namespace.marshal_with(order_model)
    @orders_namespace.doc(
        description="Delete an order"
    )
    def delete(self, order_id):
        """
            Delete an order by id
        """
        order = Order.get_by_id(order_id)
        order.delete()
        return order, HTTPStatus.OK


@orders_namespace.route('/user/<int:user_id>/order/<int:order_id>')
class GetSpecificOrderByUser(Resource):
    @orders_namespace.marshal_with(order_model)
    @jwt_required()
    def get(self, user_id, order_id):
        """
            Get a user's specific order
        """
        user = User.get_by_id(user_id)
        order = Order.get_by_id(order_id).filter_by(user_id=user.id).first()
        return order, HTTPStatus.OK


@orders_namespace.route('/user/<int:user_id>/orders')
class UserOrders(Resource):
    @orders_namespace.marshal_list_with(order_model)
    @jwt_required()
    def get(self, user_id):
        """
            Get all orders by a specific user
        """
        user = User.get_by_id(user_id)
        orders = user.orders
        return orders, HTTPStatus.OK


@orders_namespace.route('/order/status/<int:order_id>')
class UpdateOrderStatus(Resource):

    @orders_namespace.expect(order_status_model)
    @orders_namespace.marshal_with(order_model)
    def patch(self, order_id):
        """
            Update an order's status
        """
        data = orders_namespace.payload
        order_to_update = Order.get_by_id(order_id)

        order_to_update.order_status = data['order_status']

        order_to_update.commit()
        return order_to_update, HTTPStatus.OK
