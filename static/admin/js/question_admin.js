(function($) {
    'use strict';
    
    $(document).ready(function() {
        // 获取学科和单元的select元素
        var $subjectField = $('#id_subject');
        var $unitField = $('#id_unit');
        
        if ($subjectField.length && $unitField.length) {
            // 保存所有单元选项及其文本
            var allUnits = [];
            $unitField.find('option').each(function() {
                var $option = $(this);
                if ($option.val()) {  // 排除空选项
                    allUnits.push({
                        value: $option.val(),
                        text: $option.text(),
                        html: $option.clone()
                    });
                }
            });
            
            // 过滤单元函数
            function filterUnits() {
                var selectedSubject = $subjectField.val();
                var selectedSubjectText = $subjectField.find('option:selected').text();
                var currentUnit = $unitField.val();
                
                // 提取学科代码（从文本中）
                // 格式：CIE A-Level Computer Science (9618) -> 提取 cs 或 9618
                var subjectCode = '';
                if (selectedSubjectText) {
                    // 尝试从Subject的code中提取
                    var match = selectedSubjectText.match(/\(([^)]+)\)/);
                    if (match) {
                        subjectCode = match[1];
                    }
                }
                
                // 清空单元选项
                $unitField.empty();
                $unitField.append('<option value="">---------</option>');
                
                if (!selectedSubject) {
                    // 如果没有选择学科，显示所有单元
                    allUnits.forEach(function(unit) {
                        $unitField.append(unit.html.clone());
                    });
                } else {
                    // 根据选择的学科过滤单元
                    // 单元文本格式：Unit 1: Name (cs) 或 Unit 1: Name (ig)
                    var filteredUnits = allUnits.filter(function(unit) {
                        // 从单元文本中提取学科代码
                        var unitMatch = unit.text.match(/\(([^)]+)\)$/);
                        if (unitMatch) {
                            var unitSubjectCode = unitMatch[1];
                            // 尝试匹配学科代码
                            return unitSubjectCode === subjectCode || 
                                   unit.text.includes('(' + subjectCode + ')');
                        }
                        return false;
                    });
                    
                    // 如果没有找到匹配的单元，可能是学科代码格式不同，显示所有单元
                    if (filteredUnits.length === 0) {
                        console.log('No units found for subject:', selectedSubject, subjectCode);
                        console.log('Available units:', allUnits.map(u => u.text));
                        // 显示所有单元，让用户手动选择
                        filteredUnits = allUnits;
                    }
                    
                    filteredUnits.forEach(function(unit) {
                        $unitField.append(unit.html.clone());
                    });
                }
                
                // 恢复之前选择的单元（如果存在）
                if (currentUnit) {
                    $unitField.val(currentUnit);
                }
            }
            
            // 监听学科变化
            $subjectField.on('change', function() {
                filterUnits();
            });
            
            // 初始化时过滤一次
            if ($subjectField.val()) {
                filterUnits();
            }
        }
    });
})(django.jQuery);

