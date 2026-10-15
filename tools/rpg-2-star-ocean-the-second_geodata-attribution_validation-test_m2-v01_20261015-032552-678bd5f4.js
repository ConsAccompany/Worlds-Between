#!/usr/bin/env node
// Validates third-party source attribution in the M2 travel data and the geodata attribution
// manifest, and pins the travel figures so attribution edits cannot change them.
// Usage: node tools/rpg-2-star-ocean-the-second_geodata-attribution_validation-test_m2-v01_20261015-032552-678bd5f4.js
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const MANIFEST = "docs/attribution/rpg-2-star-ocean-the-second_third-party-geodata_attribution-manifest_m2-v01_20261015-032552-916697a2.json";
const STATUSES = ["stated-by-publisher", "needs-replacement-or-verification"];
const DATE = /^\d{4}-\d{2}-\d{2}$/;

const failures = [];
const check = (ok, message) => { if (!ok) failures.push(message); };
const readJson = (rel) => JSON.parse(fs.readFileSync(path.join(ROOT, rel), "utf8"));

const manifest = readJson(MANIFEST);
const travel = readJson(manifest.dataFiles.travel);
const geodata = readJson(manifest.dataFiles.mapGeodata);
const registry = readJson(manifest.dataFiles.mapPlaceRegistry);
const docText = fs.readFileSync(path.join(ROOT, manifest.document), "utf8");
check(travel.attribution && travel.attribution.manifest === MANIFEST, "travel attribution.manifest must point at the manifest");
check(travel.attribution && travel.attribution.document === manifest.document, "travel attribution.document must match the manifest");

// Figures pinned at the 2026-10-15 values; attribution work must not change them.
const EXPECTED_LOCATIONS = {
	"earth.cn.shanghai": [31.22222, 121.45806, "geonames"],
	"earth.cn.shanghai.songjiang-outskirts": [31.00583, 121.23333, "wikipedia-songjiang-district"],
	"earth.cn.liangzhu-ruins": [30.39556, 119.99083, "unesco-whc-1592"],
};
// Liangzhu cites UNESCO 1592-004 "Area of City Site" directly; the stored value must stay within 5 m of it.
const UNESCO_1592_MAPS = "https://whc.unesco.org/en/list/1592/maps/";
const UNESCO_1592_004 = [30 + 23 / 60 + 43.97 / 3600, 119 + 59 / 60 + 26.97 / 3600];
const EXPECTED_SEGMENTS = {
	"seg.car.shanghai__songjiang-outskirts": [34.8, 26, 0],
	"seg.car.shanghai__liangzhu-ruins": [187.9, 120, 0],
};
check(travel.schemaVersion === 1, "travel schemaVersion changed");
check(travel.startLocationId === "earth.cn.shanghai", "startLocationId changed");
check(travel.locations.length === 3, "location count changed");
check(travel.segments.length === 2, "segment count changed");
check(travel.routes.length === 4, "route count changed");
check(JSON.stringify(travel.routes.map((r) => [r.id, r.status, r.legs.map((l) => [l.segmentId, l.reverse])])) === JSON.stringify([
	["route.car.shanghai__songjiang-outskirts", "available", [["seg.car.shanghai__songjiang-outskirts", false]]],
	["route.car.shanghai__liangzhu-ruins", "available", [["seg.car.shanghai__liangzhu-ruins", false]]],
	["route.car.songjiang-outskirts__liangzhu-ruins.direct", "unverified", []],
	["route.car.songjiang-outskirts__liangzhu-ruins.via-shanghai", "available", [["seg.car.shanghai__songjiang-outskirts", true], ["seg.car.shanghai__liangzhu-ruins", false]]],
]), "route legs or statuses changed");

// Travel sources: each must be well formed, and no license may be asserted without publisher terms.
const travelSources = new Map();
for (const source of (travel.attribution && travel.attribution.sources) || []) {
	check(!travelSources.has(source.id), `duplicate travel source ${source.id}`);
	travelSources.set(source.id, source);
}
function checkSource(source, where) {
	const label = `${where} source ${source.id}`;
	check(/^https:\/\//.test(source.url || ""), `${label} needs an https url`);
	check(DATE.test(source.retrievedOn || ""), `${label} needs retrievedOn`);
	check(STATUSES.includes(source.licenseStatus), `${label} has unknown licenseStatus ${source.licenseStatus}`);
	if (source.licenseStatus === "stated-by-publisher") {
		check(typeof source.license === "string" && source.license !== "", `${label} needs a license`);
		check(Array.isArray(source.termsUrls) && source.termsUrls.length > 0, `${label} needs termsUrls`);
		check(DATE.test(source.termsCheckedOn || ""), `${label} needs termsCheckedOn`);
		check(typeof source.attributionRequired === "boolean", `${label} needs attributionRequired`);
		if (source.attributionRequired) {
			check(/https:\/\//.test(source.attributionText || ""), `${label} attributionText needs a link`);
			check(docText.includes(`](${source.url})`) && docText.includes(`](${source.licenseUrl})`), `${label} credit link or license link is missing from the attribution document`);
		}
	} else {
		check(source.license === null, `${label} must not assert a license while unverified`);
		check(typeof source.licenseNote === "string" && source.licenseNote !== "", `${label} needs a licenseNote`);
	}
	if (/wikipedia\.org/.test(source.url || "")) {
		check(source.license !== "CC-BY-4.0" && source.licenseStatus !== "stated-by-publisher", `${label} must not be labelled CC BY 4.0 / verified`);
	}
	if (/whc\.unesco\.org/.test(source.url || "")) {
		check(source.license === null && source.licenseStatus === "needs-replacement-or-verification", `${label} must not assert UNESCO reuse terms`);
	}
}
travelSources.forEach((source) => checkSource(source, "travel"));
const geonames = travelSources.get("geonames");
check(geonames && geonames.license === "CC-BY-4.0" && geonames.attributionRequired === true, "GeoNames must be CC-BY-4.0 with attribution required");

const used = new Set();
for (const location of travel.locations) {
	const expected = EXPECTED_LOCATIONS[location.id];
	check(expected !== undefined, `unexpected location ${location.id}`);
	if (!expected) continue;
	check(location.coordinates.lat === expected[0] && location.coordinates.lon === expected[1], `${location.id} coordinates changed`);
	const ref = location.coordinateSource || {};
	check(ref.sourceId === expected[2], `${location.id} coordinateSource.sourceId should be ${expected[2]}`);
	const source = travelSources.get(ref.sourceId);
	check(source !== undefined, `${location.id} sourceId ${ref.sourceId} is not in attribution.sources`);
	if (source) {
		check(ref.license === source.license && ref.licenseStatus === source.licenseStatus, `${location.id} license fields disagree with source ${source.id}`);
		check(DATE.test(ref.retrievedOn || "") && /^https:\/\//.test(ref.url || ""), `${location.id} coordinateSource needs url and retrievedOn`);
	}
	used.add(ref.sourceId);
}
for (const segment of travel.segments) {
	const expected = EXPECTED_SEGMENTS[segment.id];
	check(expected !== undefined, `unexpected segment ${segment.id}`);
	if (!expected) continue;
	check(segment.roadDistanceKm === expected[0] && segment.referenceDurationMinutes === expected[1] && segment.doorToDoorAllowanceMinutes === expected[2], `${segment.id} figures changed`);
	check(segment.verification.status === "preliminary-estimate", `${segment.id} verification status changed`);
	const ref = segment.verification.source || {};
	check(travelSources.has(ref.sourceId), `${segment.id} source has no known sourceId`);
	used.add(ref.sourceId);
}
travelSources.forEach((_, id) => check(used.has(id), `travel source ${id} is listed but unused`));
travelSources.forEach((source) => (source.supersedesSourceIds || []).forEach((old) => {
	check(!travelSources.has(old) && !used.has(old), `superseded source ${old} is still listed or referenced`);
}));
const liangzhu = travel.locations.find((l) => l.id === "earth.cn.liangzhu-ruins");
if (liangzhu) {
	check((liangzhu.coordinateSource || {}).url === UNESCO_1592_MAPS, "Liangzhu coordinateSource must cite the UNESCO 1592 maps table");
	const dLat = (liangzhu.coordinates.lat - UNESCO_1592_004[0]) * 111320;
	const dLon = (liangzhu.coordinates.lon - UNESCO_1592_004[1]) * 111320 * Math.cos(UNESCO_1592_004[0] * Math.PI / 180);
	check(Math.hypot(dLat, dLon) < 5, "Liangzhu coordinates are not within 5 m of UNESCO 1592-004");
}

// Manifest: covers every travel source with identical terms, plus all map geodata sources.
const manifestSources = new Map(manifest.sources.map((s) => [s.id, s]));
manifest.sources.forEach((source) => checkSource(source, "manifest"));
travelSources.forEach((source, id) => {
	const m = manifestSources.get(id);
	check(m !== undefined, `manifest lacks travel source ${id}`);
	if (m) {
		for (const key of ["url", "license", "licenseStatus", "attributionRequired", "attributionText", "retrievedOn", "licenseNote", "termsUrls", "termsCheckedOn", "supersedesSourceIds"]) {
			check(JSON.stringify(m[key]) === JSON.stringify(source[key]), `manifest ${id}.${key} differs from travel data`);
		}
	}
});
const manifestUpstreams = new Set(manifest.sources.flatMap((s) => (s.items || []).map((i) => i.upstreamUrl).filter(Boolean)));
for (const source of geodata.sources || []) {
	check(manifestUpstreams.has(source.upstream), `manifest lacks map geodata source ${source.id}`);
	check(/public domain/i.test(source.license || "") && /naturalearthdata\.com/.test(source.upstream + source.license), `map geodata source ${source.id} is not a Natural Earth public-domain source`);
}
for (const place of registry.reference_places || []) {
	check(manifestUpstreams.has((place.coordinate_source || {}).url), `manifest lacks reference place source for ${place.id}`);
}
const ne = manifestSources.get("natural-earth");
check(ne && ne.license === "public-domain" && ne.attributionRequired === false, "Natural Earth must be public-domain with attribution not required");

if (failures.length) {
	console.error(`FAIL geodata attribution validation (${failures.length})`);
	failures.forEach((f) => console.error("  - " + f));
	process.exit(1);
}
console.log(`PASS geodata attribution validation: ${travelSources.size} travel sources, ${manifest.sources.length} manifest sources, ${(geodata.sources || []).length} map geodata layers`);
