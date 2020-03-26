required_string_field = {
    'type': 'string',
    'required': True
}

required_number_field = {
    'type': 'number',
    'required': True
}

string_field = {
    'type': 'string'
}

number_field = {
    'type': 'number'
}

boolean_field = {
    'type': 'boolean'
}

list_string_field = {
    'type': 'list',
    'mapping': {'type': 'string'}
}

list_object_field = {
    'type': 'list',
    'mapping': {'type': 'dict'}
}
