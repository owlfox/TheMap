import shapefile
from lxml import etree, objectify
from pyproj import Proj, transform
from datetime import datetime
import pdb

# define Namespaces, not sure about 2.0
ns_xAL = "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
ns_gml = "http://www.opengis.net/gml"
ns_wtr = "http://www.opengis.net/citygml/waterbody/2.0"
ns_app = "http://www.opengis.net/citygml/appearance/2.0"
ns_core = "http://www.opengis.net/citygml/2.0"
ns_veg = "http://www.opengis.net/citygml/vegetation/2.0"
ns_dem = "http://www.opengis.net/citygml/relief/2.0"
ns_tran = "http://www.opengis.net/citygml/transportation/2.0"
ns_bldg = "http://www.opengis.net/citygml/building/2.0"
ns_grp = "http://www.opengis.net/citygml/cityobjectgroup/2.0"
ns_tun = "http://www.opengis.net/citygml/tunnel/2.0"
ns_frn = "http://www.opengis.net/citygml/cityfurniture/2.0"
ns_gen = "http://www.opengis.net/citygml/generics/2.0"
ns_brid = "http://www.opengis.net/citygml/bridge/2.0"
ns_xlink = "http://www.w3.org/1999/xlink"
ns_luse = "http://www.opengis.net/citygml/landuse/2.0"
ns_schemaLocation = "http://www.opengis.net/citygml/building/2.0 http://schemas.opengis.net/citygml/building/2.0/building.xsd http://www.opengis.net/citygml/cityobjectgroup/2.0 http://schemas.opengis.net/citygml/cityobjectgroup/2.0/cityObjectGroup.xsd http://www.opengis.net/citygml/tunnel/2.0 http://schemas.opengis.net/citygml/tunnel/2.0/tunnel.xsd http://www.opengis.net/citygml/waterbody/2.0 http://schemas.opengis.net/citygml/waterbody/2.0/waterBody.xsd http://www.opengis.net/citygml/appearance/2.0 http://schemas.opengis.net/citygml/appearance/2.0/appearance.xsd http://www.opengis.net/citygml/cityfurniture/2.0 http://schemas.opengis.net/citygml/cityfurniture/2.0/cityFurniture.xsd http://www.opengis.net/citygml/generics/2.0 http://schemas.opengis.net/citygml/generics/2.0/generics.xsd http://www.opengis.net/citygml/bridge/2.0 http://schemas.opengis.net/citygml/bridge/2.0/bridge.xsd http://www.opengis.net/citygml/vegetation/2.0 http://schemas.opengis.net/citygml/vegetation/2.0/vegetation.xsd http://www.opengis.net/citygml/relief/2.0 http://schemas.opengis.net/citygml/relief/2.0/relief.xsd http://www.opengis.net/citygml/transportation/2.0 http://schemas.opengis.net/citygml/transportation/2.0/transportation.xsd http://www.opengis.net/citygml/landuse/2.0 http://schemas.opengis.net/citygml/landuse/2.0/landUse.xsd"

# ns_core, ns_bldg, ns_gen, ns_gml, ns_xAL, ns_xlink, ns_xsi

nsmap = {
    'xAL': ns_xAL,
    'gml': ns_gml,
    'wtr': ns_wtr,
    'app': ns_app,
    'core': ns_core,
    'veg': ns_veg,
    'dem': ns_dem,
    'tran': ns_tran,
    'bldg': ns_bldg,
    'grp': ns_grp,
    'tun': ns_tun,
    'frn': ns_frn,
    'gen': ns_gen,
    'brid': ns_brid,
    'xlink': ns_xlink,
    'luse': ns_luse
}

proj_from = Proj(init='epsg:4326')
proj_to = Proj(init='epsg:3826')


def setSurface(bldg, surface_type="Roof"):
    roof = etree.SubElement(bldg, "{%s}boundedBy" % ns_bldg)
        
    rf = etree.SubElement(roof, "{%s}%sSurface" % (ns_bldg, surface_type))
    rflod3 = etree.SubElement(rf, "{%s}lod3MultiSurface" % ns_bldg)
    ms = etree.SubElement(rflod3, "{%s}MultiSurface" % ns_gml)
    sm = etree.SubElement(ms, "{%s}surfaceMember" % ns_gml)
    poly = etree.SubElement(sm, "{%s}Polygon" % ns_gml)
    ext = etree.SubElement(poly, "{%s}exterior" % ns_gml)
    lr = etree.SubElement(ext, "{%s}LinearRing" % ns_gml)
    psList = etree.SubElement(lr, "{%s}posList" % ns_gml, srsDimension="3")
    return psList

def iteration_buildings(cityModel, shp_layer, n=None,  ns_map={}):
    # lower corner
    point_min = (0, 0, 0)
    # upper corner
    point_max = (float("inf"), float("inf"), float("inf"))

    today = datetime.now().strftime("%Y-%m-%d")

    if n:
        the_range = range(n)
    else:
        the_range = range(len(shp_layer))
    for i in the_range:
    
        cityObjectMember = etree.SubElement(
            cityModel, "{%s}cityObjectMember" % ns_core)
        shp = shp_layer.shape(i)
        record = shp_layer.record(i).as_dict()
        bbox = shp.bbox
        height = record['H']
        build_id = str(record['ID'])
        
        bldg = etree.SubElement(cityObjectMember, "{%s}Building" % ns_bldg, {"{%s}id" % ns_gml: build_id})

        bounded = etree.SubElement(bldg, "{%s}boundedBy" % ns_gml)
        envelop = etree.SubElement(
            bounded, "{%s}Envelope" % ns_gml, srsName="EPSG:3826")
        lb = etree.SubElement(
            envelop, "{%s}lowerCorner" % ns_gml, srsDimension="3")
        ub = etree.SubElement(
            envelop, "{%s}upperCorner" % ns_gml, srsDimension="3")
        p1 = transform(proj_from, proj_to, bbox[0], bbox[1])
        p2 = transform(proj_from, proj_to, bbox[2], bbox[3])
        lb.text = "%s %s 0" % (p1[0], p1[1])
        ub.text = "%s %s %s" % (p1[0], p1[1], height)

        date = etree.SubElement(bldg, "{%s}creationDate" % ns_core)
        date.text = today
        rooftype = etree.SubElement(bldg, "{%s}roofType" % ns_bldg)
        rooftype.text = 'Flat'
        points_2D = []
        for p in shp.points:
            points_2D.append(transform(proj_from, proj_to, p[0], p[1]))
        
        polygons = get_polys(points_2D, height)
        
        psList = setSurface(bldg, surface_type="Roof")
        psList.text = " ".join("%.2f" % x for x in polygons['roof'])
        psList = setSurface(bldg, surface_type="Ground")
        psList.text = " ".join("%.2f" % x for x in polygons['ground'])
        
        for wall in polygons['walls']:
            psList = setSurface(bldg, surface_type="Wall")
            psList.text = " ".join("%.2f" % x for x in wall)
        
        
        
    return cityModel


# return roof, base, and walls
def get_polys(points_2D, height):
    polygons = {}

    
    roof = []
    ground = []
    for p in points_2D:
        roof.extend([p[0], p[1], height])
        ground.extend([p[0], p[1], 0.0])
    
    polygons['roof'] = roof    
    polygons['ground'] = roof
    
    walls = []
    for i in range(1, len(points_2D)):
        p1 = (points_2D[i-1][0], points_2D[i-1][1], 0.0)
        p2 = (points_2D[i][0], points_2D[i][1], height)
        
        wall = getwall(p1, p2)
        walls.append(wall)
        
    
    polygons['walls'] = walls
    
    return polygons

def getwall(p1, p2):
    wall = []
    wall.extend([p1[0], p1[1], p1[2]])
    wall.extend([p1[0], p1[1], p2[2]])
    wall.extend([p2[0], p2[1], p2[2]])
    wall.extend([p2[0], p2[1], p1[2]])
    wall.extend([p1[0], p1[1], p1[2]])
    return wall

def build_gml_main():


    # Main Element
    cityModel = etree.Element("{%s}CityModel" % ns_core, nsmap=nsmap)
    # Add branch
    description = etree.SubElement(cityModel, "{%s}description" % ns_gml)
    description.text = "transformed by Michael Chen 2019-11-14 from shapefile"
    name = etree.SubElement(cityModel, "{%s}name" % ns_gml)
    name.text = "Taichung City"


 
    # Read Shapefile
    shp_layer = shapefile.Reader('./tccity')

    # Add buildings
    cityModel=iteration_buildings(cityModel, shp_layer, ns_map=nsmap)



    # pretty print
    # print(etree.tostring(cityModel, pretty_print=True))

    # Save File
    et=etree.ElementTree(cityModel)
    outFile=open('./output.xml', 'wb')
    et.write(outFile, xml_declaration=True, encoding='utf-8', pretty_print=True)
    

if __name__ == '__main__':
    build_gml_main()
