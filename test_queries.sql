SELECT l.id, l.title, l.list_price
FROM listings l
JOIN listing_status ls ON l.status_id = ls.id
WHERE ls.name = 'for_sale';



SELECT u.first_name, u.last_name, u.email, ur.name AS role
FROM users u
LEFT JOIN user_roles ur ON u.id = ur.user_id;


SELECT 
    u.first_name || ' ' || u.last_name AS agent_name,
    a.title,
    ag.name AS agency_name
FROM agents a
JOIN users u ON a.user_id = u.id
JOIN agent_agencies aa ON a.id = aa.agent_id
JOIN agencies ag ON aa.agency_id = ag.id;




SELECT 
    l.title,
    loc.street_address,
    loc.city,
    p.rooms,
    p.living_area_sqm,
    l.list_price
FROM listings l
JOIN listing_properties lp ON l.id = lp.listing_id
JOIN properties p ON lp.property_id = p.id
JOIN locations loc ON p.location_id = loc.id
JOIN property_types pt ON p.property_type_id = pt.id
WHERE pt.name = 'apartment'
	AND loc.city = 'Stockholm'
  	AND p.rooms >= 3;
  
  
SELECT 
    l.title,
    loc.city,
    p.living_area_sqm,
    p.plot_area_sqm,
    l.list_price
FROM listings l
JOIN listing_properties lp ON l.id = lp.listing_id
JOIN properties p ON lp.property_id = p.id
JOIN locations loc ON p.location_id = loc.id
JOIN property_types pt ON p.property_type_id = pt.id
WHERE pt.name = 'house'
ORDER BY l.list_price DESC;




SELECT 
    l.title,
    loc.street_address,
    loc.city,
    p.monthly_fee,
    l.list_price
FROM listings l
JOIN listing_properties lp ON l.id = lp.listing_id
JOIN properties p ON lp.property_id = p.id
JOIN locations loc ON p.location_id = loc.id
JOIN tenures t ON p.tenure_id = t.id
WHERE t.name = 'bostadsratt'
	AND p.monthly_fee < 4000
ORDER BY p.monthly_fee;



SELECT 
    l.title,
    loc.city,
    p.energy_class,
    p.year_built,
    l.list_price
FROM listings l
JOIN listing_properties lp ON l.id = lp.listing_id
JOIN properties p ON lp.property_id = p.id
JOIN locations loc ON p.location_id = loc.id
WHERE p.energy_class = 'A';




SELECT 
    l.title,
    oh.starts_at,
    oh.note
FROM open_houses oh
JOIN listings l ON oh.listing_id = l.id
JOIN open_house_types oht ON oh.type_id = oht.id
WHERE oht.name = 'digital';



SELECT 
    ls.name AS status,
    COUNT(*) AS antal
FROM listings l
JOIN listing_status ls ON l.status_id = ls.id
GROUP BY ls.name
ORDER BY antal DESC;




SELECT 
    loc.city,
    COUNT(*) AS antal_objekt,
    ROUND(AVG(l.list_price)) AS snitt_pris,
    MIN(l.list_price) AS min_pris,
    MAX(l.list_price) AS max_pris
FROM listings l
JOIN listing_status ls ON l.status_id = ls.id
JOIN listing_properties lp ON l.id = lp.listing_id
JOIN properties p ON lp.property_id = p.id
JOIN locations loc ON p.location_id = loc.id
WHERE ls.name = 'for_sale'
GROUP BY loc.city
ORDER BY snitt_pris DESC;




SELECT 
    pt.name AS bostadstyp,
    COUNT(*) AS antal
FROM properties p
JOIN property_types pt ON p.property_type_id = pt.id
GROUP BY pt.name
ORDER BY antal DESC;




SELECT 
    pt.name AS bostadstyp,
    ROUND(AVG(p.living_area_sqm), 1) AS snitt_boyta,
    ROUND(AVG(p.rooms), 1) AS snitt_rum
FROM properties p
JOIN property_types pt ON p.property_type_id = pt.id
GROUP BY pt.name;




SELECT 
    loc.city,
    ROUND(AVG(l.list_price / NULLIF(p.living_area_sqm, 0))) AS kvm_pris
FROM listings l
JOIN listing_status ls ON l.status_id = ls.id
JOIN listing_properties lp ON l.id = lp.listing_id
JOIN properties p ON lp.property_id = p.id
JOIN locations loc ON p.location_id = loc.id
WHERE ls.name = 'for_sale'
  	AND p.living_area_sqm > 0
GROUP BY loc.city
ORDER BY kvm_pris DESC;



SELECT 
    u.first_name || ' ' || u.last_name AS maklare,
    ag.name AS byra,
    COUNT(l.id) AS antal_objekt,
    SUM(l.list_price) AS totalt_varde
FROM agents a
JOIN users u ON a.user_id = u.id
JOIN agent_agencies aa ON a.id = aa.agent_id
JOIN agencies ag ON aa.agency_id = ag.id
JOIN listing_agents la ON a.id = la.agent_id
JOIN listings l ON la.listing_id = l.id
JOIN listing_status ls ON l.status_id = ls.id
WHERE ls.name = 'for_sale'
GROUP BY u.first_name, u.last_name, ag.name
ORDER BY antal_objekt DESC;


SELECT 
    u.first_name || ' ' || u.last_name AS maklare,
    COUNT(*) AS antal_salda
FROM agents a
JOIN users u ON a.user_id = u.id
JOIN listing_agents la ON a.id = la.agent_id
JOIN listings l ON la.listing_id = l.id
JOIN listing_status ls ON l.status_id = ls.id
WHERE ls.name = 'sold'
GROUP BY u.first_name, u.last_name;




SELECT 
    u.first_name || ' ' || u.last_name AS anvandare,
    l.title,
    loc.city,
    l.list_price,
    sl.created_at AS sparad_datum
FROM saved_listings sl
JOIN users u ON sl.user_id = u.id
JOIN listings l ON sl.listing_id = l.id
JOIN listing_properties lp ON l.id = lp.listing_id
JOIN properties p ON lp.property_id = p.id
JOIN locations loc ON p.location_id = loc.id
WHERE u.id = 1
ORDER BY sl.created_at DESC;



SELECT 
    u.first_name || ' ' || u.last_name AS anvandare,
    COUNT(sl.id) AS antal_sparade
FROM users u
LEFT JOIN saved_listings sl ON u.id = sl.user_id
GROUP BY u.id, u.first_name, u.last_name
HAVING COUNT(sl.id) > 0
ORDER BY antal_sparade DESC;




SELECT 
    u.first_name || ' ' || u.last_name AS anvandare,
    u.email,
    ss.name AS soknamn
FROM saved_searches ss
JOIN users u ON ss.user_id = u.id
WHERE ss.send_email = TRUE;




SELECT 
    l.title,
    COUNT(CASE WHEN mt.name = 'image' THEN 1 END) AS antal_bilder,
    COUNT(CASE WHEN mt.name = 'floorplan' THEN 1 END) AS antal_planritningar,
    COUNT(CASE WHEN mt.name = 'video' THEN 1 END) AS antal_videos
FROM listings l
LEFT JOIN listing_media lm ON l.id = lm.listing_id
LEFT JOIN media_types mt ON lm.media_type_id = mt.id
GROUP BY l.id, l.title
ORDER BY antal_bilder DESC;



SELECT l.id, l.title
FROM listings l
LEFT JOIN listing_media lm ON l.id = lm.listing_id
WHERE lm.id IS NULL;




SELECT 
    l.id,
    l.title,
    l.description,
    ls.name AS status,
    l.list_price,
    pt.name AS bostadstyp,
    t.name AS upplatelseform,
    p.rooms,
    p.living_area_sqm,
    p.floor,
    p.monthly_fee,
    p.energy_class,
    p.year_built,
    loc.street_address,
    loc.postal_code,
    loc.city,
    loc.municipality,
    u.first_name || ' ' || u.last_name AS maklare,
    u.phone AS maklare_telefon,
    ag.name AS byra
FROM listings l
JOIN listing_status ls ON l.status_id = ls.id
JOIN listing_properties lp ON l.id = lp.listing_id
JOIN properties p ON lp.property_id = p.id
JOIN property_types pt ON p.property_type_id = pt.id
JOIN tenures t ON p.tenure_id = t.id
JOIN locations loc ON p.location_id = loc.id
JOIN listing_agents la ON l.id = la.listing_id
JOIN agents a ON la.agent_id = a.id
JOIN users u ON a.user_id = u.id
JOIN agent_agencies aa ON a.id = aa.agent_id
JOIN agencies ag ON aa.agency_id = ag.id
WHERE l.id = 1;


SELECT 
    l.title,
    loc.city,
    pt.name AS typ,
    p.rooms,
    p.living_area_sqm,
	l.list_price
FROM listings l
JOIN listing_status ls ON l.status_id = ls.id
JOIN listing_properties lp ON l.id = lp.listing_id
JOIN properties p ON lp.property_id = p.id
JOIN property_types pt ON p.property_type_id = pt.id
JOIN locations loc ON p.location_id = loc.id
WHERE ls.name = 'for_sale'
  	AND l.list_price BETWEEN 2000000 AND 6000000
  	AND p.rooms >= 2
  	AND p.living_area_sqm >= 60
ORDER BY l.list_price;



