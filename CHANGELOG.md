# Changelog

## v0.1.3 (2024/10/07)
### 🐛 Fixes
- [Ensure all calls to O365 library methods are async](https://github.com/RogerSelwyn/MS365-ToDo/commit/57439a7f2ee9058e0a438cfc2726e96a6314ae03) - @RogerSelwyn
- [Don't update todo if status is being changed](https://github.com/RogerSelwyn/MS365-ToDo/commit/1c359f71fcd4f3124300cdbba95d2de9241c63f0) - @RogerSelwyn

### 📚 Documentation
- [Capitalization for valid URL](https://github.com/RogerSelwyn/MS365-ToDo/commit/e72a3b071957a0c74abfe790159c8920fc615ee5) - @adam-allmer

### 🔖 Release
- [Release v0.1.3](https://github.com/RogerSelwyn/MS365-ToDo/commit/90f2d7261279768e4632be78fbe6f35d80126ea6) - @RogerSelwyn

## v0.1.2 (2024/09/04)
### 🐛 Fixes
- [Fix issue of o365 library accessing token within the event loop](https://github.com/RogerSelwyn/MS365-ToDo/commit/1fae1a788d960edc6b9e01f9b5cc9b848dcff341) - @RogerSelwyn

### 🧰 Maintenance
- [Implement Sourcery.ai recomendations](https://github.com/RogerSelwyn/MS365-ToDo/commit/48edfa39e37484cbe3a6371f098bc895e8860bbc) - @RogerSelwyn

### 🔖 Release
- [Release v0.1.2](https://github.com/RogerSelwyn/MS365-ToDo/commit/cd1b9c8c4d4a70b428fa75f45e85823aeb432da7) - @RogerSelwyn

## v0.1.1 (2024/08/13)
### 🐛 Fixes
- [Handle corrupted token file gracefully with repair](https://github.com/RogerSelwyn/MS365-ToDo/commit/f054ffa414b0405e409bb78fc60c4e43aaab2df5) - @RogerSelwyn
- [Extraneous letter](https://github.com/RogerSelwyn/MS365-ToDo/commit/d95c08d7f9553f0a269ca8d1f6bae09abe7ffdb8) - @RogerSelwyn

### 🧰 Maintenance
- [Move coordinator setup code to new _async_setup method](https://github.com/RogerSelwyn/MS365-ToDo/commit/72be021f12887f6b6ac65b1827d2940f7d59cea6) - @RogerSelwyn
- [Minimum HA version 2024.8.0](https://github.com/RogerSelwyn/MS365-ToDo/commit/84aeb02d4b89630a737a9ac3fad8fce9b7e45dab) - @RogerSelwyn

### 🔖 Release
- [Release v0.1.1](https://github.com/RogerSelwyn/MS365-ToDo/commit/aa4cf23d156c9ee05af6c816709fc1d5a8015d35) - @RogerSelwyn

## v0.1.0 (2024/07/18)
### ✨ Enhancements
- [Add diagnostics support](https://github.com/RogerSelwyn/MS365-ToDo/commit/9ed9c2ac1fb917d533403404ab70f31fc29414b9) - @RogerSelwyn

### 🧰 Maintenance
- [Code updates in support of standardisation across MS365 integrations](https://github.com/RogerSelwyn/MS365-ToDo/commit/6271f197d6fded7e26563b40192cc216d657b429) - @RogerSelwyn
- [Consolidate sensor code to one place](https://github.com/RogerSelwyn/MS365-ToDo/commit/1314391a6a0b0d0e4ded92d935be68fd0b7653c8) - @RogerSelwyn
- [Consolidate duplicate code](https://github.com/RogerSelwyn/MS365-ToDo/commit/4f054a9904ce82df23292938cc09ede29d817b51) - @RogerSelwyn

### 🔖 Release
- [Release v0.1.0](https://github.com/RogerSelwyn/MS365-ToDo/commit/a03892c7029435354aa713fda4cebd890be47c43) - @RogerSelwyn

## v0.0.4 (2024/07/08)
### 🐛 Fixes
- [Fix incorrect Due date shown for To Do](https://github.com/RogerSelwyn/MS365-ToDo/commit/66660f94f2e04db7eaa8e3184ca62849c87aea98) - @RogerSelwyn

### 🧰 Maintenance
- [Update codeql.yml](https://github.com/RogerSelwyn/MS365-ToDo/commit/ebd812891b07d06ad01be72519847944ab6e2250) - @RogerSelwyn
- [Remove use of internal attribute](https://github.com/RogerSelwyn/MS365-ToDo/commit/294cfac9cd802f309ed14ab24c6901ff51d59a6a) - @RogerSelwyn

### ⬆️ Dependencies
- [Bump O365 to 2.0.35](https://github.com/RogerSelwyn/MS365-ToDo/commit/c67b16a271913b126370d2f9dfa23c307b067ce1) - @RogerSelwyn
- [Bump O365 to 2.0.36](https://github.com/RogerSelwyn/MS365-ToDo/commit/fd793c0628b42179bd844a5559c151e3f39915d0) - @RogerSelwyn
- [Auto update requirements.txt](https://github.com/RogerSelwyn/MS365-ToDo/commit/8a9b9693a66bc274e06f427b42d00efeb355e6b4) - @actions-user

### 📚 Documentation
- [Update CHANGELOG.md](https://github.com/RogerSelwyn/MS365-ToDo/commit/10409964a8de6bde592af7af3ea8ed643e7eaf39) - @RogerSelwyn
- [Update README.md](https://github.com/RogerSelwyn/MS365-ToDo/commit/3e04a2adc96e9cfac6904d78c976193693c67f29) - @RogerSelwyn

### 🔖 Release
- [Release v0.0.4](https://github.com/RogerSelwyn/MS365-ToDo/commit/bf71a0463ed5e96a316d68886cdaa8f9773bf8e5) - @RogerSelwyn


## v0.0.3 (2024/06/04)
### 💥 Breaking Changes
- [Standardise entity name](https://github.com/RogerSelwyn/MS365-ToDo/commit/c6c12eac2649ef8435cd85e0e86df30e47328ea4) - @RogerSelwyn

### 🧰 Maintenance
- [Rename account_name to entity_name](https://github.com/RogerSelwyn/MS365-ToDo/commit/7cff96025aae170cf7ba7b8c88d989146e1ec2ea) - @RogerSelwyn
- [Add translations for services](https://github.com/RogerSelwyn/MS365-ToDo/commit/cd4a598bdd535ba358cb2f04ece52f18d61a9be2) - @RogerSelwyn

### 📚 Documentation
- [Updates](https://github.com/RogerSelwyn/MS365-ToDo/commit/30830342a68c5662cb723e0c05dd4315bc9f40b4) - @RogerSelwyn
- [Tweak](https://github.com/RogerSelwyn/MS365-ToDo/commit/2cc89912dcb5470125f124b3b5c26b3d83bf93d3) - @RogerSelwyn

### 🔖 Release
- [Release v0.0.3](https://github.com/RogerSelwyn/MS365-ToDo/commit/4584f3b38e23c4529d847c398a43f330b13d8eef) - @RogerSelwyn

## v0.0.2 (2024/06/03)
### 💥 Breaking Changes
- [Renamed account_name to entity_name](https://github.com/RogerSelwyn/MS365-ToDo/commit/43747a9265129ab7d1fb314944e3211a8b61c0d2) - @RogerSelwyn

### 🧰 Maintenance
- [Change Azure to Entra ID](https://github.com/RogerSelwyn/MS365-ToDo/commit/b3b260d9c43246cd61487e34871a8c861443930d) - @RogerSelwyn
- [Remove unrequired code](https://github.com/RogerSelwyn/MS365-ToDo/commit/713555fd5a4c1caf27c25fa78389182b661871df) - @RogerSelwyn
- [Update todo.md](https://github.com/RogerSelwyn/MS365-ToDo/commit/5af6b23f3a7e6d6d876afb4aec4df4b14c68a0ef) - @RogerSelwyn

### 🔖 Release
- [Release v0.0.2](https://github.com/RogerSelwyn/MS365-ToDo/commit/c13b564aa5b26f69a2a8723655d9228af6af9520) - @RogerSelwyn

## v0.0.1 (2024/06/02)
Initial release

