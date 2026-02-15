local wezterm = require 'wezterm'
local config = {}
if wezterm.config_builder then
    config = wezterm.config_builder()
end

config.automatically_reload_config = true

if wezterm.target_triple == 'x86_64-pc-windows-msvc' then
    config.initial_cols = 160
    config.initial_rows = 40
    config.font_size = 12.0
else
    config.initial_cols = 80
    config.initial_rows = 24
    config.font_size = 12.0
end

config.window_background_opacity = 0.8

config.font = wezterm.font_with_fallback{
    'JetBrainsMono Nerd Font',
    'Noto Sans CJK SC',
    'monospace'
}

config.cursor_blink_rate = 0
config.default_cursor_style = 'SteadyBlock'

local appearance = wezterm.gui.get_appearance()
if appearance:find "Dark" then
    config.color_scheme = "Catppuccin Macchiato"
else
    config.color_scheme = "Catppuccin Latte"
end

-- if true then
--     config.color_scheme = 'Tokyo Night'
-- else
--     config.color_scheme = 'Midsummer Night'
--     config.colors = {
--         foreground = '#C6B8B1',
--         background = '#1C1E26',
--         cursor_fg = '#1C1E26',
--         cursor_bg = '#D34C6B',
--         cursor_border = '#D34C6B',
--         selection_fg = '#C6B8B1',
--         selection_bg = '#2E303E',
--         ansi = {
--             '#000000',
--             '#D85069',
--             '#2DCBBE',
--             '#E5A382',
--             '#35A5BB',
--             '#D34C68',
--             '#2DCBBE',
--             '#B1C7C9',
--         },
--         brights = {
--             '#666666',
--             '#D85069',
--             '#2DCBBE',
--             '#E5A382',
--             '#35A5BB',
--             '#D34C68',
--             '#2DCBBE',
--             '#B1C7C9',
--         },
--         tab_bar = {
--             active_tab = {
--                 bg_color = '#B1C7C9',
--                 fg_color = '#1C1E26',
--             },
--             inactive_tab = {
--                 bg_color = '#1C1E26',
--                 fg_color = '#879596',
--             },
--         },
--     }
-- end

config.scrollback_lines = 2000
config.enable_scroll_bar = false
config.min_scroll_bar_height = '2cell'

config.hide_tab_bar_if_only_one_tab = true
config.exit_behavior = 'Close'
config.window_close_confirmation = 'NeverPrompt'

local ssh_domains = {}
for host, _ in pairs(wezterm.enumerate_ssh_hosts()) do
    table.insert(ssh_domains, {
        name = host,
        remote_address = host,
        assume_shell = 'Posix',
    })
end
config.ssh_domains = ssh_domains

if wezterm.target_triple == 'x86_64-pc-windows-msvc' then
    config.default_gui_startup_args = { 'connect', 'MDD' }
end

return config
