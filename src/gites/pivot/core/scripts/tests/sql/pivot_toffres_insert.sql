INSERT INTO toffres VALUES ('CGT_0002_00000C26', 'LA TURBINE', 'LA TURBINE', 'LA TURBINE', 'LA TURBINE', null, null, 'Chansin', null, '10', null, '5530', 1239, '91038', null, null, 'Durnal', 'Yvoir', 'Namur', 'Hors Parcs', 'Haute-Meuse Dinantaise', 193087, 112762, 4.97255, 50.3248, null, null, null, null, 'Pas de lab̩lisation', '3 ̩pis', 3, 8, 8, 3, null, 'Chalet pour jeux d''enfants.', null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 0, null, 0, 0, '2009-10-19 10:45:12', '2014-06-02 00:00:00', 2, null, null, '503321679', 'GRNA1153');
INSERT INTO toffres VALUES ('GIT-01-000OQA', 'LES OISEAUX', 'LES OISEAUX', 'LES OISEAUX', 'LES OISEAUX', null, null, 'Rue de Burdinne', null, '5 A', null, '4217', 619, '61028', null, null, 'H̩ron', 'H̩ron', 'Li̬ge', 'Parc naturel des Vall̩es de la Burdinale et de la M̩haigne', 'Vall̩es de la Burdinale et de la Mehaigne', 201545, 138529, 5.09487, 50.5558, null, null, null, null, 'Pas de lab̩lisation', '3 ̩pis', 3, 1, 5, 2, null, 'Terrain de pétanque disponible.', null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 0, null, 0, 1, '2012-06-06 14:52:04', '2014-05-18 15:14:46', 2, null, null, null, null);
INSERT INTO toffres VALUES
    ('CGT_0002_00000007',
    'LES CARDAMINES',
    'LES CARDAMINES',
    'LES CARDAMINES',
    'LES CARDAMINES',
    null,
    null,
    'Comognes de Temploux',
    null,
    '16',
    null,
    '5020',
    1466,
    '92123',
    null,
    null,
    'Temploux',
    'Namur',
    'Namur',
    'Hors Parcs',
    'Pays de Namur',
    177719,
    129147,
    4.75796,
    50.473,
    null,
    null,
    null,
    null,
    'Pas de labélisation',
    '2 épis',
    2,
    2,
    4,
    1,
    null,
    'LES CARDAMINES Gîte rural aménagé, avec poutres',
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    0,
    null,
    0,
    1,
    '2009-10-19 09:05:49',
    '2014-02-04 15:17:55',
    2,
    null,
    null,
    '503321699',
    'GRNA5403');

INSERT
	INTO ttarifs(id_tarif,
	categorie,
	type,
	type_nl,
	type_en,
	type_de,
	complement_info,
	complement_info_nl,
	complement_info_en,
	complement_info_de,
	date,
	prix_min,
	prix_max,
	fk_toffres_codeCGT)
VALUES
	(12515334,
	0,
	'Haute saison - (Semaine)',
	'Hoogseizoen - (Week)',
	null,
	null,
	null,
	null,
	null,
	null,
	'2014-06-02',
	250,
	null,
	'CGT_0002_00000C26');

INSERT
	INTO ttarifs(id_tarif,
	categorie,
	type,
	type_nl,
	type_en,
	type_de,
	complement_info,
	complement_info_nl,
	complement_info_en,
	complement_info_de,
	date,
	prix_min,
	prix_max,
	fk_toffres_codeCGT)
VALUES
	(12215334,
	0,
	'Haute saison - (Semaine)',
	'Hoogseizoen - (Week)',
	null,
	null,
	null,
	null,
	null,
	null,
	'2014-03-02',
	190,
	null,
	'CGT_0002_00000C26');

INSERT
	INTO tcontacts(id_contact,
	civilite,
	nom,
	prenom,
	adresse,
	numero,
	boite,
	id_ins,
	ins,
	cp,
	localite,
	commune,
	telephone,
	fax,
	gsm,
	email,
	url)
VALUES
	(10017528,
	'Monsieur',
	'FIVET',
	'Louis',
	'Chansin',
	'10',
	null,
	null,
	null,
	'5530',
	'Durnal',
	'Yvoir',
	'+3283690167',
	'+3283690167',
	'+32477904980',
	'laturbine@hotmail.com',
	null);

INSERT
	INTO treloffrecontact(fk_toffres_codeCGT,
	fk_tcontacts_id_contact,
	type,
	type_nl,
	type_en,
	type_de)
VALUES
	('CGT_0002_00000C26',
	10017528,
	'Propriétaire',
	null,
	null,
	null);
INSERT
	INTO treloffrecontact(fk_toffres_codeCGT,
	fk_tcontacts_id_contact,
	type,
	type_nl,
	type_en,
	type_de)
VALUES
	('CGT_0002_00000C26',
	10017528,
	'Propriétaire',
	null,
	null,
	null);
