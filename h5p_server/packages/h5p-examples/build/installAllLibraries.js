"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
require("dotenv/config");
const path = require("path");
const _i18next = require("i18next");
const i18next = _i18next.default || _i18next;
const _i18nextFs = require("i18next-fs-backend");
const i18nextFsBackend = _i18nextFs.default || _i18nextFs;
const H5P = require("@lumieducation/h5p-server");
const createH5PEditor_1 = require("./createH5PEditor");
const User_1 = require("./User");

async function main() {
    console.log("Initializing H5P Editor for batch library installation...");
    const translationFunction = await i18next
        .use(i18nextFsBackend)
        .init({
            backend: {
                loadPath: path.join(__dirname, "../../../node_modules/@lumieducation/h5p-server/build/assets/translations/{{ns}}/{{lng}}.json")
            },
            defaultNS: "server",
            fallbackLng: "en",
            ns: ["server", "hub"]
        });
    const config = await new H5P.H5PConfig(new H5P.fsImplementations.JsonStorage(path.join(__dirname, "../config.json"))).load();
    const h5pEditor = await (0, createH5PEditor_1.default)(
        config,
        path.join(__dirname, "../h5p/libraries"),
        path.join(__dirname, "../h5p/content"),
        path.join(__dirname, "../h5p/temporary-storage"),
        path.join(__dirname, "../h5p/user-data"),
        (key, language) => translationFunction(key, { lng: language })
    );
    const user = new User_1.default("1", "System Administrator", "admin@kolibri.local");

    console.log("Fetching Content Type Cache from H5P Hub...");
    const allContentTypes = await h5pEditor.contentTypeCache.get();
    console.log(`Discovered ${allContentTypes.length} content types on H5P Hub.`);

    const installedLibsWrapped = await h5pEditor.libraryManager.listInstalledLibraries();
    const installedMachineNames = new Set(Object.keys(installedLibsWrapped));
    console.log(`Currently installed libraries: ${installedMachineNames.size}`);

    const contentTypesToInstall = [
        "H5P.InteractiveVideo",
        "H5P.CoursePresentation",
        "H5P.BranchingScenario",
        "H5P.InteractiveBook",
        "H5P.Column",
        "H5P.Accordion",
        "H5P.Dialogcards",
        "H5P.DragQuestion",
        "H5P.DragText",
        "H5P.FindTheWords",
        "H5P.ImageHotspots",
        "H5P.MemoryGame",
        "H5P.MultiChoice",
        "H5P.QuestionSet",
        "H5P.SingleChoiceSet",
        "H5P.TrueFalse",
        "H5P.Summary",
        "H5P.Timeline",
        "H5P.Essay",
        "H5P.Agamotto",
        "H5P.ImageSlider",
        "H5P.ImageJuxtaposition",
        "H5P.Dictation",
        "H5P.Flashcards",
        "H5P.AudioRecorder",
        "H5P.SpeakTheWords",
        "H5P.Chart",
        "H5P.Collage",
        "H5P.PersonalityQuiz",
        "H5P.ImageMultipleHotspotQuestion",
        "H5P.ImageChoice",
        "H5P.SortParagraphs",
        "H5P.KewArCode"
    ];

    for (const ct of allContentTypes) {
        if (!contentTypesToInstall.includes(ct.machineName) && ct.machineName !== "H5P.IFrameEmbed") {
            contentTypesToInstall.push(ct.machineName);
        }
    }

    console.log(`Total content types to process: ${contentTypesToInstall.length}`);

    let successCount = 0;
    let skipCount = 0;
    let failCount = 0;

    for (const machineName of contentTypesToInstall) {
        if (installedMachineNames.has(machineName)) {
            console.log(`[EXISTS] ${machineName}`);
            skipCount++;
            continue;
        }
        try {
            console.log(`[FETCHING] ${machineName}...`);
            const results = await h5pEditor.installLibraryFromHub(machineName, user);
            console.log(`[INSTALLED] ${machineName} (+${results.length} dependencies)`);
            successCount++;
        } catch (err) {
            console.warn(`[FAILED/SKIPPED] ${machineName}: ${err.message || err}`);
            failCount++;
        }
    }

    console.log(`\nLibrary installation completed: ${successCount} installed, ${skipCount} already existed, ${failCount} failed.`);
}

main().catch(err => {
    console.error("Fatal error installing libraries:", err);
    process.exit(1);
});
