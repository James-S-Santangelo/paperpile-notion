from typing import Dict, List


def match(string, candidates) -> str:
    for c in candidates:
        if c in string:
            return c
    return None


def format_entry(entry: Dict[str, str], journals: List[Dict[str, str]], conferences: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """ Produces a dictionary in format column_name: {type: x, value: y} for each value in the entry"""
    # Select the conference shortname based on proceedings
    if entry['Item type'] == 'Journal Article':
        if 'Full journal' in entry.keys() and entry['Full journal']:
            venue = [j['short'] for j in journals if j['name'] == entry['Full journal'].strip()]
        else:
            venue = [j['short'] for j in journals if j['name'] == entry['Journal'].strip()]
        if not venue:
            venue = [entry['Journal'].strip()[:100]]
    elif entry['Item type'] == 'Conference Paper':
        venue = [
            c['short'] for c in conferences if c['name'] == match(
            entry['Proceedings title'].strip().replace('{','').replace('}',''), [c['name'] for c in conferences]
        )]
        if not venue:
            venue = [entry['Proceedings title'].strip()[:100]]
    elif entry['Item type'] == 'Preprint Manuscript':
        if "openreview" in entry['URLs'].strip().split(';')[0]:
            venue = ["OpenReview"]
        else:
            venue = [entry['Archive prefix'].strip()]
    elif entry['Item type'] == 'Book Chapter':
        venue = [entry['Book title'].strip()]
    elif entry['Item type'] == 'Book':
        venue = [entry['Title'].strip()]
    # Arxiv links are privileged
    links = [x for x in entry['URLs'].strip().split(';')]
    arxiv_links = [x for x in links if 'arxiv' in x]
    if len(arxiv_links) > 0:
        selected_link = arxiv_links[0]
        venue.append('arXiv')
    else:
        selected_link = links[0]
    # Multichoice don't accept commas and maybe other punctuation, too
    for i, v in enumerate(venue):
        exclude = set([','])
        venue[i] = ''.join(ch for ch in v if ch not in exclude)
    year = entry['Publication year'].strip()
    all_labels = [x.strip() for x in entry['Labels filed in'].strip().split(';')]
    fields = [x.split(' - ')[1] for x in all_labels if x.startswith('FLD')]
    methods = [x.split(' - ')[1] for x in all_labels if x.startswith('MET')]
    study_system = [x.split(' - ')[1] for x in all_labels if x.startswith('SS')]
    topics = [x.split(' - ')[1] for x in all_labels if x.startswith('TOP')]
    formatted_entry = {
        'Item type':        {'type': 'select',       'value': entry['Item type'].strip()},
        'Authors':          {'type': 'multi_select', 'value': entry['Authors'].strip().split(',')},
        'Title':            {'type': 'title',        'value': entry['Title'].strip().replace('{','').replace('}','')},
        'Venues':           {'type': 'multi_select', 'value': venue},
        'Year':             {'type': 'select',       'value': year},
        'Link':             {'type': 'url',          'value': selected_link},
        'Fields':           {'type': 'multi_select', 'value': fields},#, 'color': [COLOR_MAP[cat]['color'] for cat in categories]}
        'Methods':          {'type': 'multi_select', 'value': methods},
        'Study System':     {'type': 'multi_select', 'value': study_system},
        'Topics':           {'type': 'multi_select', 'value': topics},
    }
    if not 'to read' in entry['Folders filed in'].lower():  
        formatted_entry['Status'] = {'type': 'select', 'value': 'Done'}
    return formatted_entry
