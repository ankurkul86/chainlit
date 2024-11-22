import yaml
import json
import re



def get_endpoints(openapi_data):
    """Extract endpoints along with their summary and description."""
    endpoints = []
    paths = openapi_data.get('paths', {})

    for path, methods in paths.items():
        for method, details in methods.items():
            endpoint_info = {
                'path': path,
                'method': method.upper(),
                'summary': details.get('summary', ''),
                'description': details.get('description', '')
            }
            endpoints.append(endpoint_info)

    # Convert the list of endpoints to a JSON string
    return json.dumps(endpoints, indent=2)


def list_types(type_name, openapi_spec):
    """
    Lists all items under a specified type in the OpenAPI specification, either 'components' or 'paths'.

    :param openapi_spec: The OpenAPI specification as a dictionary.
    :param type_name: The type to list (e.g., 'schemas', 'parameters' for components, or 'paths' for paths).
    :return: A list of matching items, either components or paths.
    """
    if type_name == 'paths':
        # Return the list of all paths
        return list(openapi_spec.get('paths', {}).keys())
    
    # Otherwise, check within the components section
    components = openapi_spec.get('components', {})
    if type_name in components:
        return list(components[type_name].keys())

    return []



def get_details(value, openapi_spec):
    """
    Retrieves the details of a specific value from both 'paths' and reusable sections (components, definitions, etc.)
    in the OpenAPI specification, considering both OpenAPI 2.0 and 3.0 structures.

    :param openapi_spec: The OpenAPI specification as a dictionary.
    :param value: The specific name of the path, component, or operation to retrieve.
    :return: A JSON string containing the details of the specified value,
             or None if not found.
    """
    # Check for version
    is_openapi_3 = 'openapi' in openapi_spec and openapi_spec['openapi'].startswith('3.')
    is_openapi_2 = 'swagger' in openapi_spec and openapi_spec['swagger'] == '2.0'

    # Check if the value exists in paths (same in both 2.0 and 3.0)
    paths = openapi_spec.get('paths', {})
    if value in paths:
        return json.dumps({value: paths[value]}, indent=2)

    # OpenAPI 3.0 components handling
    if is_openapi_3:
        components = openapi_spec.get('components', {})
        for component_type, component_dict in components.items():
            if value in component_dict:
                return json.dumps({component_type: {value: component_dict[value]}}, indent=2)

    # OpenAPI 2.0 handling (definitions, parameters, responses, securityDefinitions)
    if is_openapi_2:
        # Check definitions (equivalent to schemas in 3.0)
        definitions = openapi_spec.get('definitions', {})
        if value in definitions:
            return json.dumps({'definitions': {value: definitions[value]}}, indent=2)

        # Check parameters (equivalent to parameters in 3.0 components)
        parameters = openapi_spec.get('parameters', {})
        if value in parameters:
            return json.dumps({'parameters': {value: parameters[value]}}, indent=2)

        # Check responses (equivalent to responses in 3.0 components)
        responses = openapi_spec.get('responses', {})
        if value in responses:
            return json.dumps({'responses': {value: responses[value]}}, indent=2)

        # Check securityDefinitions (equivalent to securitySchemes in 3.0 components)
        security_definitions = openapi_spec.get('securityDefinitions', {})
        if value in security_definitions:
            return json.dumps({'securityDefinitions': {value: security_definitions[value]}}, indent=2)

    return None



def extract_single_json(text):
    # Regular expression to find JSON-like content, handling newlines
    json_pattern = r'\{(?:[^{}]|\n|.)*?\}'

    # Search for the first JSON string in the text
    match = re.search(json_pattern, text)
    
    if match:
        json_str = match.group()  # Extract the matched JSON string
        try:
            # Parse the JSON string into a Python object
            json_obj = json.loads(json_str)
            return json_obj
        except json.JSONDecodeError:
            print("Found JSON-like content but failed to decode it.")
            return None
    else:
        print("No JSON found in the text.")
        return None
    


def load_api_file(file_path):
    
    with open(file_path, 'r', encoding='utf-8') as file:
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return yaml.safe_load(file)
        elif file_path.endswith('.json'):
            return json.load(file)
        else:
            raise ValueError("Unsupported file format")