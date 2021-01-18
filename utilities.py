def ensure_has_attribute(obj, attr):
    if not hasattr(obj, attr):
        raise AttributeError("No such attribute:", attr)


def store_in_config(config, entity):
    (attr, section_name) = entity.get_section_info()
    config[section_name] = {}
    section = config[section_name]
    for attr in entity.get_section_attributes():
        ensure_has_attribute(entity, attr)
        section[attr] = str(getattr(entity, attr))


def load_from_section(config, section_name, entity):
    (attr, attr_value) = entity.get_section_info()
    section = config[section_name]
    setattr(entity, attr, section_name)
    for attr in entity.get_section_attributes():
        ensure_has_attribute(entity, attr)
        setattr(entity, attr, section[attr])
    entity.reformat()
    return entity


def remove_from_config(config, section_name):
    config.remove_section(section_name)


# finds all sections in the specified config which meet given criterias
# if the entity_creator is None, then it returns list of the section names which meet the criterias specified
# otherwise it returns list of entities loaded from those sections, entity_creator should create empty_entities, which
#   will be filled with the info from the section
def find_in_config(config, criterias, entity_creator=None):
    result = []
    for section_name in config.sections():
        if meets_criterias(config, section_name, criterias):
            if entity_creator is None:
                result.append(section_name)
            else:
                result.append(load_from_section(config, section_name, entity_creator()))
    return result


def meets_criterias(config, section_name, criterias):
    section = config[section_name]
    for (attr, predicate) in criterias:
        if attr is None:
            if not predicate(section_name):
                return False
        elif not predicate(section[attr]):
            return False
    return True


def store_config(config, path):
    with open(path, 'w') as configfile:
        config.write(configfile)


def string_to_list(str_list):
    if str_list == "[]":
        return []
    else:
        return str_list.strip('\'][').split('\', \'')


def string_to_set(str_set):
    if str_set == "set()" or str_set == "{}":
        return set()
    else:
        return str_set.strip("'}{").split("', '")