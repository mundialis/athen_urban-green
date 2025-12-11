# Processing
Contains actinia process chains and process chain templates
Within the docker container necessary GRASS projects are created in [`start.sh`](../docker/start.sh) if not existing.

## Use actinia process chain

### Run process via actinia processing endpoint
Start process chain from outside docker container, from the top level of the directory:
```bash
curl -X POST -H 'Content-Type: application/json' -H 'accept: application/json' -u actinia:actinia -d @processing/pc_athens_t_modules.json http://0.0.0.0:8088/api/v3/locations/latlong_wgs84/processing_export

# or if you have `actiniapost` defined in `.bashrc`, use:

actiniapost actinia:actinia processing/pc_athens_t_modules.json http://0.0.0.0:8088/api/v3/locations/latlong_wgs84/processing_export
```

To check the status of processing use the status request, e.g.
```bash
curl -u actinia:actinia http://0.0.0.0:8088/api/v3/resources/actinia/resource_id-<RESOURCE-ID>
```


<!-- ### Run process via actinia_modules processing endpoint
Using this endpoint requires `projects` to be defined inside the template for actinia to know in which GRASS GIS project to run the process.
Also the process chain template needs to be available inside actinia.
To do so, register the template:

```bash
curl -X POST -H 'Content-Type: application/json' -H 'accept: application/json' -u actinia:actinia -d @processing/modules_endpoint/template_athen_urban-green.json http://0.0.0.0:8088/api/v3/actinia_templates
```
Or if it exists already, it can be updated via
```bash
curl -X PUT -H 'Content-Type: application/json' -H 'accept: application/json' -u actinia:actinia -d @processing/modules_endpoint/template_athen_urban-green.json http://0.0.0.0:8088/api/v3/actinia_templates/athen_urban-green
```
Above steps describe how to register a user template. Later in the project, the template might be registered as a global template, so that this step can be skipped.

Check if everything looks correct:
- http://0.0.0.0:8088/api/v3/actinia_templates/athen_urban-green
- http://0.0.0.0:8088/api/v3/actinia_modules/athen_urban-green

Now to start the process, only the GeoJSON needs to be posted:
```bash
curl -X POST -H 'Content-Type: application/json' -H 'accept: application/json' -u actinia:actinia -d @processing/input/dummy_company_locations.geojson http://0.0.0.0:8088/api/v3/actinia_modules/athen_urban-green/process
```
 You will need to enter the actinia username and password. -->

### Check status of processing
A) in browser:
copy status url from response and paste to a browser, remove the `s` from `https` and press enter

B) via command line:
copy ID from response and insert below
`curl -u actinia:actinia http://0.0.0.0:8088/api/v3/resources/actinia/resource_id-<ID>` | jq