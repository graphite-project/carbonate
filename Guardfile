guard 'shell' do
  watch(/carbonate\/(.*).py$/) {|m| `script/test` }
  watch(/tests\/(.*).py$/) {|m| `script/test` }
end
